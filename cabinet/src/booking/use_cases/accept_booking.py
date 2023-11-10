from typing import Any

from common.sentry.utils import send_sentry_log
from src.booking.exceptions import BookingNotFoundError
from src.booking.repos import Booking, BookingRepo
from src.booking.entities import BaseBookingCase
from src.task_management.constants import OnlineBookingSlug, FastBookingSlug
from src.task_management.utils import get_booking_tasks


class AcceptBookingCase(BaseBookingCase):
    """
    Кейс подтверждения договора офферты
    """

    def __init__(
        self,
        booking_repo: type[BookingRepo],
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()

    async def __call__(self, user_id: int, booking_id: int) -> Booking:
        booking_filters: dict = dict(id=booking_id, user_id=user_id, contract_accepted=False, active=True)
        booking: Booking = await self.booking_repo.retrieve(filters=booking_filters)
        if not booking:
            sentry_ctx: dict[str, Any] = dict(
                booking_id=booking_id,
                user_id=user_id,
                booking_filters=booking_filters,
                ex=BookingNotFoundError,
            )
            await send_sentry_log(
                tag="AcceptBookingCase",
                message="Booking not found",
                context=sentry_ctx,
            )
            raise BookingNotFoundError
        booking: Booking = await self.booking_repo.update(model=booking, data=dict(contract_accepted=True))
        await booking.fetch_related(
            "building",
            "ddu__participants",
            "project__city",
            "property__section",
            "property__property_type",
            "amocrm_status__group_status",
            "floor",
            "agent",
            "agency",
            "booking_source",
        )
        interested_task_chains: list[str] = [
            OnlineBookingSlug.ACCEPT_OFFER.value,
            FastBookingSlug.ACCEPT_OFFER.value,
        ]
        booking.tasks = await get_booking_tasks(
            booking_id=booking.id, task_chain_slug=interested_task_chains
        )
        return booking
