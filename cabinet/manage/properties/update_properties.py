# pylint: disable=broad-except,redefined-builtin
from asyncio import Future, ensure_future, gather
from copy import copy
from typing import Any, Callable, Type

from common.backend import repos as backend_repos
from common.utils import from_global_id, to_global_id
from config import tortoise_config
from src.buildings import repos as building_repos
from src.floors import repos as floors_repos
from src.projects import repos as projects_repos
from src.properties import repos as properties_repos
from src.properties.services import ImportPropertyService
from tortoise import Model, Tortoise


class UpdatePropertiesManage:
    """
    Обновление всех квартир с портала
    """
    def __init__(self) -> None:
        self.service: Callable = ImportPropertyService(
            global_id_encoder=to_global_id,
            global_id_decoder=from_global_id,
            floor_repo=floors_repos.FloorRepo,
            project_repo=projects_repos.ProjectRepo,
            building_repo=building_repos.BuildingRepo,
            property_repo=properties_repos.PropertyRepo,
            building_booking_type_repo=building_repos.BuildingBookingTypeRepo,
            backend_building_booking_type_repo=backend_repos.BackendBuildingBookingTypesRepo,
            backend_properties_repo=backend_repos.BackendPropertiesRepo,
            backend_floors_repo=backend_repos.BackendFloorsRepo,
            backend_sections_repo=backend_repos.BackendSectionsRepo,
        )
        self.property_repo: properties_repos.PropertyRepo = properties_repos.PropertyRepo()

        self.orm_class: Type[Tortoise] = Tortoise
        self.orm_config: dict[str, Any] = copy(tortoise_config)
        self.orm_config.pop("generate_schemas", None)

    async def __call__(self, *args, **kwargs) -> None:
        await self.orm_class.init(config=self.orm_config)
        futures: list[Future] = []
        properties: list[Model] = await self.property_repo.list()
        for property in properties:
            futures.append(ensure_future(self.import_property(property_id=property.id)))
        await gather(*futures)
        await self.orm_class.close_connections()

    async def import_property(self, property_id: int) -> None:
        try:
            await self.service(property_id=property_id)
        except Exception:
            pass
