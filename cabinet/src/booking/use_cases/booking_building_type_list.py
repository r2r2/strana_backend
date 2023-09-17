from typing import List, Type

from ..entities import BaseBookingBuildingTypeListCase, BaseBookingBuildingTypeModel
from src.booking.repos import BookingRepo
from src.booking.exceptions import BookingNotFoundError


class BookingBuildingTypeListCase(BaseBookingBuildingTypeListCase):
    """
    Список типов условий оплаты
    """
    def __init__(
            self,
            booking_repo: Type[BookingRepo],
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()

    async def __call__(self, booking_id: int) -> List[BaseBookingBuildingTypeModel]:
        booking = await self.booking_repo.retrieve(
            filters=dict(id=booking_id),
            related_fields=['building'],
        )
        if booking is None:
            raise BookingNotFoundError

        return await booking.building.booking_types
