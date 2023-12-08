from asyncio import sleep

from config import lk_admin_config
from src.booking.services import UpdateAmoBookingService
from ..entities import BaseBookingCase


class SuperuserBookingFillDataCase(BaseBookingCase):
    """
    Обновление сделок в АмоСРМ после изменения в админке брокера.
    """

    def __init__(
        self,
        export_booking_in_amo_service: UpdateAmoBookingService,
    ) -> None:
        self.export_booking_in_amo_service: UpdateAmoBookingService = export_booking_in_amo_service

    async def __call__(
        self,
        booking_id: int,
        data: str,
    ) -> None:

        if data == lk_admin_config["admin_export_key"]:
            await sleep(3)
            await self.export_booking_in_amo_service(booking_id=booking_id)
