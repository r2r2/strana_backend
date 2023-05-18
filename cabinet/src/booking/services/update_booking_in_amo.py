from typing import Any, NamedTuple, Optional, Type

from ..entities import BaseBookingCase
from ..mixins import BookingLogMixin
from ..repos import Booking
from ..types import BookingAmoCRM


class BookingTypeNamedTuple(NamedTuple):
    price: int
    amocrm_id: Optional[int] = None


class UpdateAmoBookingService(BaseBookingCase, BookingLogMixin):
    """
    Обновление сделок в АмоСРМ после изменения в админке брокера.
    """

    def __init__(
        self,
        create_amocrm_log_task: Any,
        amocrm_class: Type[BookingAmoCRM],
    ) -> None:
        self.amocrm_class: Type[BookingAmoCRM] = amocrm_class
        self.create_amocrm_log_task: Any = create_amocrm_log_task

    async def __call__(
        self,
        booking: Booking,
    ) -> None:
        async with await self.amocrm_class() as amocrm:
            await self._update_booking_data(booking, amocrm)

    async def _update_booking_data(self, booking: Booking, amocrm: BookingAmoCRM) -> int:
        """
        Обновление данных сделки в АмоСРМ.
        """

        lead_options: dict[str, Any] = dict(
            lead_id=booking.amocrm_id,
            status_id=booking.amocrm_status_id,
            company=booking.agency.amocrm_id if booking.agency else None,
            contacts=[booking.agent.amocrm_id] if booking.agent else None,
            online_purchase_id=booking.online_purchase_id,
        )

        await amocrm.update_lead(**lead_options)

        note_data: dict[str, Any] = dict(
            element="lead",
            lead_id=booking.amocrm_id,
            note="lead_changed",
            text="Изменены данные сделки в админке",
        )
        self.create_amocrm_log_task.delay(note_data=note_data)
