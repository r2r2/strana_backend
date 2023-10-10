from common.backend.repos import BackendBuildingBookingTypesRepo
from src.buildings.repos import BuildingBookingTypeRepo
from ..entities import BasePropertyService


class ImportBuildingBookingTypesService(BasePropertyService):
    def __init__(
        self,
        building_booking_type_repo: type[BuildingBookingTypeRepo],
        backend_building_booking_type_repo: type[BackendBuildingBookingTypesRepo],
    ):
        self.building_booking_type_repo: BuildingBookingTypeRepo = building_booking_type_repo()
        self.backend_building_booking_type_repo: BackendBuildingBookingTypesRepo = backend_building_booking_type_repo()

    async def __call__(self):
        backend_building_booking_types = await self.backend_building_booking_type_repo.list()
        created_building_booking_type_ids: set[int] = set()
        for backend_building_booking_type in backend_building_booking_types:
            created_building_booking_type_ids.add(backend_building_booking_type.id)
            await self.building_booking_type_repo.update_or_create(
                data=dict(
                    id=backend_building_booking_type.id,
                    price=backend_building_booking_type.price,
                    period=backend_building_booking_type.period,
                    amocrm_id=backend_building_booking_type.amocrm_id,
                ),
                filters=dict(pk=backend_building_booking_type.id),
            )
        building_booking_type_ids: set[int] = set(
            await self.building_booking_type_repo.list().distinct().values_list("id", flat=True)
        )
        removed_building_booking_type_ids = building_booking_type_ids - created_building_booking_type_ids
        for building_booking_type_id in removed_building_booking_type_ids:
            filters = dict(id=building_booking_type_id)
            building_booking_type = await self.building_booking_type_repo.retrieve(filters=filters)
            await self.building_booking_type_repo.delete(building_booking_type)
