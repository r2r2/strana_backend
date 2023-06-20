from typing import Any

from src.booking.constants import BookingSubstages
from src.booking.exceptions import BookingNotFoundError
from src.booking.loggers import booking_changes_logger
from src.booking.services.deactivate_booking import DeactivateBookingService
from src.properties.entities import BasePropertyCase
from src.booking.repos import BookingRepo, Booking
from src.properties.models import RequestUnbindBookingPropertyModel


class UnbindBookingPropertyCase(BasePropertyCase):
    """
    Отвязывание объекта недвижимости от сделки
    """
    def __init__(
        self,
        booking_repo: type[BookingRepo],
        deactivate_booking_service: DeactivateBookingService,
    ):
        self.booking_repo: BookingRepo = booking_repo()
        self.deactivate_booking_service: DeactivateBookingService = deactivate_booking_service
        self.booking_update = booking_changes_logger(
            self.booking_repo.update, self, content="Отвязывание объекта недвижимости от сделки"
        )

    async def __call__(self, payload: RequestUnbindBookingPropertyModel) -> None:
        filters: dict[str, int] = dict(id=payload.booking_id)
        booking: Booking = await self.booking_repo.retrieve(filters=filters)
        if not booking:
            raise BookingNotFoundError
        await self.deactivate_booking_service(booking=booking)
        data: dict[str, Any] = dict(
            profitbase_booked=False,
            amocrm_substage=BookingSubstages.MAKE_DECISION,
        )
        await self.booking_update(booking=booking, data=data)
