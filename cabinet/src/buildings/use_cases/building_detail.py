from tortoise.queryset import QuerySet
from tortoise.query_utils import Q

from src.projects.repos import ProjectRepo
from src.floors.repos import FloorRepo
from common.backend.repos import BackendPropertiesRepo
from src.projects.constants import PropertyBackendType
from src.properties.constants import PropertyStatuses, PropertyTypes
from ..entities import BaseBuildingCase
from ..repos import BuildingRepo, BuildingSectionRepo


class BuildingDetailCase(BaseBuildingCase):
    """
    Получение корпуса
    """
    def __init__(
        self,
        building_repo: type[BuildingRepo],
        project_repo: type[ProjectRepo],
        building_section_repo: type[BuildingSectionRepo],
        floor_repo: type[FloorRepo],
        backend_properties_repo: type[BackendPropertiesRepo],
    ) -> None:
        self.building_repo: BuildingRepo = building_repo()
        self.project_repo: ProjectRepo = project_repo()
        self.building_section_repo: BuildingSectionRepo = building_section_repo()
        self.floor_repo: FloorRepo = floor_repo()
        self.backend_properties_repo: BackendPropertiesRepo = backend_properties_repo()

    async def __call__(self, building_id: int):
        floor_qs: QuerySet = self.floor_repo.list(
            annotations=self.get_floor_set_annotations
        )
        section_qs: QuerySet = self.building_section_repo.list(
            prefetch_fields=[
                dict(relation="section_floors", queryset=floor_qs, to_attr="floor_set"),
            ],
            annotations=self.get_section_set_annotations
        )
        building = await self.building_repo.retrieve(
            filters=dict(id=building_id),
            annotations=self.get_buildings_annotations,
            prefetch_fields=[
                "project",
                dict(relation="building_section", queryset=section_qs, to_attr="section_set"),
            ],
        )

        # количество свободных квартир корпуса из бекенда портала
        flats_count = await self.backend_properties_repo.list(
            filters=dict(
                building__name=building.name,
                type=PropertyBackendType.FLAT,
                status=PropertyStatuses.FREE,
            ),
            related_fields=["project"],
        ).count()
        building.flats_count = flats_count

        return building


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
