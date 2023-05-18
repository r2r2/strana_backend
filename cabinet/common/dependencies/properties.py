from typing import Type, Optional

from fastapi import Body

from common import utils
from common.backend.repos import BackendBuildingBookingTypesRepo
from src.buildings.repos import BuildingRepo, BuildingBookingTypeRepo
from src.floors.repos import FloorRepo
from src.projects.repos import ProjectRepo
from src.properties.repos import PropertyRepo, Property
from src.properties.services import ImportPropertyService
from common.backend import repos as backend_repos


class PropertiesFromGlobalId:
    """Get property ids from global property ids"""
    def __init__(
            self,
            properties_repo: Type[PropertyRepo],
            import_property_service: Optional[ImportPropertyService] = None
    ):
        self.properties_repo = properties_repo()
        if not import_property_service:
            # should be loaded from di-container but now its creating an instance if dep is not provided
            import_property_service = ImportPropertyService(
                floor_repo=FloorRepo,
                global_id_decoder=utils.from_global_id,
                global_id_encoder=utils.to_global_id,
                project_repo=ProjectRepo,
                building_repo=BuildingRepo,
                property_repo=PropertyRepo,
                building_booking_type_repo=BuildingBookingTypeRepo,
                backend_building_booking_type_repo=BackendBuildingBookingTypesRepo,
                backend_properties_repo=backend_repos.BackendPropertiesRepo,
                backend_floors_repo=backend_repos.BackendFloorsRepo,
                backend_sections_repo=backend_repos.BackendSectionsRepo,
                backend_special_offers_repo=backend_repos.BackendSpecialOfferRepo,
            )
        self.import_property_service: ImportPropertyService = import_property_service

    async def __call__(
            self, property_global_ids: list[str] = Body(..., embed=True)
    ) -> list[int]:
        res_ids = []
        global_ids = set(property_global_ids)
        for global_id in global_ids:
            res_ids.append(await self._create_or_update_backend_property(global_id))
        return res_ids

    async def _create_or_update_backend_property(self, global_id) -> int:
        """
        Cоздаем или обновляем объект по данным из БД портала
        """
        data = dict(global_id=global_id)
        property = await self.properties_repo.retrieve(filters=data)
        if not property:
            property = await self.properties_repo.create(data)

        await self.import_property_service(property=property)
        return property.id
