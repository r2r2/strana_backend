from typing import Any

from src.amocrm.repos import AmocrmStatus, AmocrmStatusRepo
from src.booking.constants import BookingSubstages
from src.booking.exceptions import BookingNotFoundError
from src.booking.loggers import booking_changes_logger
from src.booking.services.deactivate_booking import DeactivateBookingService
from src.properties.entities import BasePropertyCase
from src.booking.repos import BookingRepo, Booking
from src.properties.models import RequestUnbindBookingPropertyModel
from src.task_management.constants import PaidBookingSlug
from src.task_management.services import UpdateTaskInstanceStatusService


class UnbindBookingPropertyCase(BasePropertyCase):
    """
    Отвязывание объекта недвижимости от сделки
    """
    def __init__(
        self,
        booking_repo: type[BookingRepo],
        deactivate_booking_service: DeactivateBookingService,
        update_status_service: UpdateTaskInstanceStatusService,
        amocrm_status_repo: type[AmocrmStatusRepo],
    ):
        self.booking_repo: BookingRepo = booking_repo()
        self.amocrm_status_repo: AmocrmStatusRepo = amocrm_status_repo()
        self.deactivate_booking_service: DeactivateBookingService = deactivate_booking_service
        self.update_status_service: UpdateTaskInstanceStatusService = update_status_service
        self.booking_update = booking_changes_logger(
            self.booking_repo.update, self, content="Отвязывание объекта недвижимости от сделки"
        )

    async def __call__(self, payload: RequestUnbindBookingPropertyModel) -> None:
        filters: dict[str, int] = dict(id=payload.booking_id)
        booking: Booking = await self.booking_repo.retrieve(
            filters=filters,
            related_fields=["project"],
        )
        if not booking:
            raise BookingNotFoundError
        await self.deactivate_booking_service(booking=booking)

        filters = dict(
            name__iexact=BookingSubstages.MAKE_DECISION_LABEL,
            pipeline_id=booking.project.amo_pipeline_id,
        )
        amocrm_status: AmocrmStatus = await self.amocrm_status_repo.retrieve(filters=filters)

        data: dict[str, Any] = dict(
            profitbase_booked=False,
            amocrm_substage=BookingSubstages.MAKE_DECISION,
            property=None,
            amocrm_status=amocrm_status,
            active=False,
        )

        await self.booking_update(booking=booking, data=data)
        await self.update_status_service(booking_id=booking.id, status_slug=PaidBookingSlug.START.value)
