from typing import Type

from tortoise.query_utils import Q

from src.properties.repos import PropertyRepo
from src.properties.constants import PropertyStatuses, PropertyTypes
from ..entities import BaseProjectCase
from ..repos import Project, ProjectRepo
from ..exceptions import ProjectNotFoundError


class ProjectDetailCase(BaseProjectCase):
    """
    Кейс получения проекта
    """
    def __init__(
            self,
            project_repo: Type[ProjectRepo],
            property_repo: Type[PropertyRepo]
    ) -> None:
        self.project_repo: ProjectRepo = project_repo()
        self.property_repo: PropertyRepo = property_repo()

    async def __call__(self, project_id: int) -> Project:
        project: Project = await self.project_repo.retrieve(
            filters=dict(id=project_id),
            prefetch_fields=["city", "metro", "transport"],
            annotations=self.get_project_annotations,
        )
        if not project:
            raise ProjectNotFoundError
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
            # количество свободных квартир
            flats_count=self.project_repo.a_builder.build_count(
                "properties",
                filter=Q(
                    properties__type=PropertyTypes.FLAT,
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
