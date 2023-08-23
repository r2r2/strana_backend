from typing import List, Type

from ..entities import BaseBookingBuildingTypeListCase, BaseBookingBuildingTypeModel
from src.buildings.repos import BuildingRepo, BuildingBookingTypeRepo


class BookingBuildingTypeListCase(BaseBookingBuildingTypeListCase):
    """
    Список типов условий оплаты
    """
    def __init__(
            self,
            building_repo: Type[BuildingRepo],
            building_booking_type_repo: Type[BuildingBookingTypeRepo],
    ) -> None:
        self.building_repo: BuildingRepo = building_repo()
        self.building_booking_type_repo: BuildingBookingTypeRepo = building_booking_type_repo()

    async def __call__(self, building_id: int) -> List[BaseBookingBuildingTypeModel]:

        building = await self.building_repo.retrieve(filters=dict(id=building_id))

        return await building.booking_types
