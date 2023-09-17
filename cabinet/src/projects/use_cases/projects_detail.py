from typing import Type

from tortoise.expressions import Q

from common.backend.repos import BackendPropertiesRepo
from src.properties.repos import PropertyRepo
from src.properties.constants import PropertyStatuses, PropertyTypes
from ..entities import BaseProjectCase
from ..repos import Project, ProjectRepo
from ..exceptions import ProjectNotFoundError
from ..constants import PropertyBackendType


class ProjectDetailCase(BaseProjectCase):
    """
    Кейс получения проекта
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

    async def __call__(self, project_id: int) -> Project:
        project: Project = await self.project_repo.retrieve(
            filters=dict(id=project_id),
            prefetch_fields=["city", "metro", "transport"],
            annotations=self.get_project_annotations,
        )
        if not project:
            raise ProjectNotFoundError

        # количество свободных квартир проекта из бекенда портала
        flats_count = await self.backend_properties_repo.list(
            filters=dict(
                project__slug=project.slug,
                type=PropertyBackendType.FLAT,
                status=PropertyStatuses.FREE,
            ),
            related_fields=["project"],
        ).count()
        project.flats_count = flats_count

        return project

    @property
    def get_project_annotations(self) -> dict:
        """
        Агрегация для проекта
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
