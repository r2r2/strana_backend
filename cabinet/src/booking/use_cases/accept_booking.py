from src.booking.exceptions import BookingNotFoundError
from src.booking.repos import Booking, BookingRepo
from ..entities import BaseBookingCase


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
            raise BookingNotFoundError
        return await self.booking_repo.update(model=booking, data=dict(contract_accepted=True))
