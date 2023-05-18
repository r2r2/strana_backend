import datetime
from typing import Any, Type
import zlib

from ..entities import BaseBookingCase
from ..exceptions import BookingNotFoundError
from ..repos import BookingRepo, Booking


class SuperuserBookingFillDataCase(BaseBookingCase):
    """
    Обновление сделок в АмоСРМ после изменения в админке брокера.
    """

    def __init__(
        self,
        booking_repo: Type[BookingRepo],
        update_booking_service: Any,
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.update_booking_service: Any = update_booking_service

    async def __call__(
        self,
        booking_id: int,
        data: int,
    ) -> Booking:
        booking: Booking = await self.booking_repo.retrieve(
            filters=dict(id=booking_id),
            related_fields=["project", "user", "property", "agency", "agent"]
        )
        if not booking:
            raise BookingNotFoundError

        hash_date = zlib.crc32(bytes(str(datetime.datetime.now().date()), 'utf-8'))

        if booking.amocrm_id and data == hash_date:
            await self.update_booking_service(booking=booking)

        return booking
