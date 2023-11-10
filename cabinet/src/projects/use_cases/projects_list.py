from typing import Any, Optional, Type

from tortoise.expressions import Q

from common.backend.repos import BackendPropertiesRepo
from src.properties.repos import PropertyRepo
from src.properties.constants import PropertyStatuses, PropertyTypes
from ..constants import ProjectStatus
from ..entities import BaseProjectCase
from ..models import Status
from ..repos import Project, ProjectRepo
from ..types import ProjectPagination
from ..constants import PropertyBackendType

from src.getdoc.repos import AdditionalAgreementTemplateRepo


class ProjectsListCase(BaseProjectCase):
    """
    Список проектов
    """

    def __init__(self, project_repo: Type[ProjectRepo]) -> None:
        self.project_repo: ProjectRepo = project_repo()

    async def __call__(self, status: Optional[Status], pagination: ProjectPagination) -> dict[str, Any]:
        filters = dict(
            is_active=True,
            status=status.value,
        ) if status else dict(is_active=True, status__not=Status.COMPLETED.value)
        
        projects: list[Project] = await self.project_repo.list(
            filters=filters,
            end=pagination.end,
            start=pagination.start,
            related_fields=["city"],
        )
        unique_projects = list({project.name: project for project in projects}.values())
        count: int = await self.project_repo.count(filters=filters)
        data: dict[str, Any] = dict(count=count, result=unique_projects, page_info=pagination(count=count))
        return data


class AdditionalProjectsListCase(BaseProjectCase):
    """
    Список проектов (для api v2)
    """
    def __init__(
        self,
        project_repo: Type[ProjectRepo],
        additional_template_repo: Type[AdditionalAgreementTemplateRepo]
    ) -> None:
        self.project_repo: ProjectRepo = project_repo()
        self.additional_template_repo: AdditionalAgreementTemplateRepo = additional_template_repo()

    async def __call__(self, status: Optional[Status]) -> list[Project]:
        filters = dict(
            is_active=True,
            status=status.value,
        ) if status else dict(is_active=True, status__not=Status.COMPLETED.value)

        additional_templates_filters: dict[str, Any] = dict(
            project_id=self.project_repo.a_builder.build_outer("id")
        )
        additional_templates_qs: Any = self.additional_template_repo.list(filters=additional_templates_filters)
        annotations = dict(has_additional_templates=self.project_repo.a_builder.build_exists(additional_templates_qs))

        projects: list[Project] = await self.project_repo.list(
            filters=filters,
            annotations=annotations,
            related_fields=["city"],
        )

        unique_projects = list({project.name: project for project in projects}.values())

        return unique_projects


class ProjectsListV3Case(BaseProjectCase):
    """
    Список проектов (для api v3)
    """
    def __init__(
        self,
        project_repo: Type[ProjectRepo],
        property_repo: Type[PropertyRepo],
        backend_properties_repo: Type[BackendPropertiesRepo],
    ) -> None:
        self.project_repo: ProjectRepo = project_repo()
        self.property_repo: PropertyRepo = property_repo()
        self.backend_properties_repo: BackendPropertiesRepo = backend_properties_repo()

    async def __call__(self) -> list[Project]:
        filters = dict(
            is_active=True,
            show_in_paid_booking=True,
            status=ProjectStatus.CURRENT,
        )

        projects: list[Project] = await self.project_repo.list(
            filters=filters,
            prefetch_fields=["city", "metro", "transport"],
            annotations=self.get_projects_annotations,
        )

        # количество свободных квартир проекта из бекенда портала
        for project in projects:
            flats_count = await self.backend_properties_repo.list(
                filters=dict(
                    project__slug=project.slug,
                    type=PropertyBackendType.FLAT,
                    status=PropertyStatuses.FREE,
                ),
                related_fields=["project"],
            ).count()
            project.flats_count = flats_count

        return projects

    @property
    def get_projects_annotations(self) -> dict:
        """
        Агрегация для проектов
        """
        annotations: dict = dict(
            # количество свободных коммерческих помещений
            commercial_count=self.project_repo.a_builder.build_count(
                "properties",
                filter=Q(
                    properties__type=PropertyTypes.COMMERCIAL,
                    properties__status=PropertyStatuses.FREE
                )
            ),
            # количество свободных паркингов и кладовых
            parking_pantry_count=self.project_repo.a_builder.build_count(
                "properties",
                filter=Q(
                    properties__type__in=[PropertyTypes.PARKING, PropertyTypes.PANTRY],
                    properties__status=PropertyStatuses.FREE,
                )
            ),
        )
        return annotations
