# pylint: disable=inconsistent-return-statements
from typing import Any, Optional, Type

from src.booking.entities import BaseBookingCase
from src.booking.maintenance import amocrm_sms_maintenance
from src.booking.repos import Booking, BookingRepo


class AmoCRMSmsWebhookCase(BaseBookingCase):
    """
    Вебхук для отправки смс главному контакту сделки
    """

    def __init__(
        self,
        booking_repo: Type[BookingRepo],
        fast_booking_webhook_case: BaseBookingCase,
    ):
        self.booking_repo = booking_repo()
        self.fast_booking_webhook_case: BaseBookingCase = fast_booking_webhook_case

    @amocrm_sms_maintenance
    async def __call__(self, amocrm_id: int) -> None:
        """
        Отправка смс
        """
        fast_booking_data: dict[str, Any] = dict(amocrm_id=amocrm_id)
        booking: Optional[Booking] = await self.booking_repo.retrieve(filters=dict(amocrm_id=amocrm_id))

        if booking:
            fast_booking_data.update(booking=booking)
        await self.fast_booking_webhook_case(**fast_booking_data)
