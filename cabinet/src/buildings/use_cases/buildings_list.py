from tortoise.query_utils import Q
from tortoise.queryset import QuerySet

from src.projects.repos import ProjectRepo
from src.floors.repos import FloorRepo
from src.properties.constants import PropertyStatuses, PropertyTypes
from ..constants import BuildingTypeRequest
from ..entities import BaseBuildingCase
from ..repos import BuildingRepo, Building, BuildingSectionRepo


class BuildingsListCase(BaseBuildingCase):
    """
    Список корпусов
    """
    def __init__(
            self,
            building_repo: type[BuildingRepo],
            project_repo: type[ProjectRepo],
            building_section_repo: type[BuildingSectionRepo],
            floor_repo: type[FloorRepo],
    ) -> None:
        self.building_repo: BuildingRepo = building_repo()
        self.project_repo: ProjectRepo = project_repo()
        self.building_section_repo: BuildingSectionRepo = building_section_repo()
        self.floor_repo: FloorRepo = floor_repo()

    async def __call__(self, project_slug: str, kind: BuildingTypeRequest):
        floor_qs: QuerySet = self.floor_repo.list(
            annotations=self.get_floor_set_annotations
        )
        section_qs: QuerySet = self.building_section_repo.list(
            prefetch_fields=[
                dict(relation="section_floors", queryset=floor_qs, to_attr="floor_set"),
            ],
            annotations=self.get_section_set_annotations
        )
        building_filters: dict = dict(project__slug=project_slug, show_in_paid_booking=True, kind=kind.value)
        buildings: list[Building] = await self.building_repo.list(
            filters=building_filters,
            annotations=self.get_buildings_annotations,
            prefetch_fields=[
                "project",
                dict(relation="building_section", queryset=section_qs, to_attr="section_set"),
            ]
        )
        return buildings

    @property
    def get_buildings_annotations(self) -> dict:
        """
        Агрегация для корпуса по квартирам проекта
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
            # количество свободных паркингов
            parking_count=self.building_repo.a_builder.build_count(
                "properties",
                filter=Q(
                    properties__type__in=[PropertyTypes.PARKING],
                    properties__status=PropertyStatuses.FREE,
                )
            ),
        )
        return annotations

    @property
    def get_section_set_annotations(self) -> dict:
        """
        Агрегация для секций корпуса
        """
        annotations: dict = dict(
            # количество свободных квартир в секции
            flats_count=self.building_section_repo.a_builder.build_count(
                "building__properties",
                filter=Q(
                    building__properties__type=PropertyTypes.FLAT,
                    building__properties__status=PropertyStatuses.FREE
                )
            ),
        )
        return annotations

    @property
    def get_floor_set_annotations(self) -> dict:
        """
        Агрегация для этажей секции корпуса
        """
        annotations: dict = dict(
            # количество свободных квартир в секции
            flats_count=self.floor_repo.a_builder.build_count(
                "properties",
                filter=Q(
                    properties__type=PropertyTypes.FLAT,
                    properties__status=PropertyStatuses.FREE
                )
            ),
            # количество свободных коммерческих помещений в секции
            commercial_count=self.floor_repo.a_builder.build_count(
                "properties",
                filter=Q(
                    properties__type=PropertyTypes.COMMERCIAL,
                    properties__status=PropertyStatuses.FREE
                )
            ),
        )
        return annotations
