from typing import Any, Optional, Type

from ..entities import BaseProjectCase
from ..models import Status
from ..repos import Project, ProjectRepo
from ..types import ProjectPagination

from src.getdoc.repos import AdditionalAgreementTemplateRepo


class ProjectsListCase(BaseProjectCase):
    """
    Список проектов
    """

    def __init__(self, project_repo: Type[ProjectRepo]) -> None:
        self.project_repo: ProjectRepo = project_repo()

    async def __call__(self, status: Optional[Status], pagination: ProjectPagination) -> dict[str, Any]:
        filters = dict(is_active=True, status=status.value) if status else dict(is_active=True)
        projects: list[Project] = await self.project_repo.list(
            filters=filters,
            end=pagination.end,
            start=pagination.start,
            related_fields=["city"],
        )
        count_list: list[tuple[int]] = await self.project_repo.count(filters=filters)
        count = count_list[0][0]
        data: dict[str, Any] = dict(count=count, result=projects, page_info=pagination(count=count))
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
        filters = dict(is_active=True, status=status.value) if status else dict(is_active=True)

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

        return projects
