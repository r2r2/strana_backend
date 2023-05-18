from typing import Any, Type

from ..entities import BaseBookingCase
from ..exceptions import BookingNotFoundError
from ..repos import Booking, BookingRepo
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
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()

        self.session: BookingSession = session

        self.document_key: str = session_config["document_key"]

    async def __call__(self, booking_id: int, user_id: int) -> Booking:
        filters: dict[str, Any] = dict(active=True, id=booking_id, user_id=user_id)
        booking: Booking = await self.booking_repo.retrieve(
            filters=filters,
            related_fields=["project", "property", "floor", "building", "ddu", "agent", "agency"],
            prefetch_fields=["ddu__participants"],
        )
        if not booking:
            raise BookingNotFoundError
        try:
            payment_amount = int(booking.payment_amount)
        except TypeError:
            payment_amount = None
        self.session[self.document_key]: str = dict(
            city=booking.project.city if booking.project else None,
            address=booking.building.address if booking.building else None,
            price=payment_amount,
            period=booking.booking_period,
            premise=booking.property.premise.label if booking.property else None,
        )
        await self.session.insert()
        return booking
