from typing import Any, Optional, Type

from ..constants import BookingCreatedSources
from ..entities import BaseBookingCase
from ..exceptions import (BookingNotFoundError, BookingTimeOutError,
                          BookingTimeOutRepeatError)
from ..repos import Booking, BookingRepo, BookingTag, BookingTagRepo
from ..types import BookingSession


class BookingRetrieveCase(BaseBookingCase):
    """
    Детальное бронирование
    """

    def __init__(
        self,
        session: BookingSession,
        session_config: dict[str, Any],
        booking_repo: Type[BookingRepo],
        booking_tag_repo: Type[BookingTagRepo],
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.booking_tag_repo: BookingTagRepo = booking_tag_repo()

        self.session: BookingSession = session

        self.document_key: str = session_config["document_key"]

    async def __call__(self, booking_id: int, user_id: int) -> Booking:
        filters: dict[str, Any] = dict(id=booking_id, user_id=user_id)
        booking: Booking = await self.booking_repo.retrieve(
            filters=filters,
            related_fields=[
                "project",
                "project__city",
                "property",
                "property__section",
                "property__property_type",
                "floor",
                "building",
                "ddu",
                "agent",
                "agency",
            ],
            prefetch_fields=["ddu__participants", "amocrm_status__group_status"],
        )
        if not booking:
            raise BookingNotFoundError
        if not booking.time_valid():
            if booking.created_source in [BookingCreatedSources.LK]:
                raise BookingTimeOutRepeatError
            raise BookingTimeOutError
        try:
            payment_amount = int(booking.payment_amount)
        except TypeError:
            payment_amount = None
        booking.booking_tags = await self._get_booking_tags(booking)
        self.session[self.document_key]: str = dict(
            city=booking.project.city.slug if booking.project else None,
            address=booking.building.address if booking.building else None,
            price=payment_amount,
            period=booking.booking_period,
            premise=booking.property.premise.label if booking.property else None,
        )
        await self.session.insert()

        return booking

    async def _get_booking_tags(self, booking: Booking) -> Optional[list[BookingTag]]:
        tag_filters: dict[str, Any] = dict(
            is_active=True,
            group_statuses=booking.amocrm_status.group_status if booking.amocrm_status else None,
        )
        return (await self.booking_tag_repo.list(filters=tag_filters, ordering='-priority')) or None
