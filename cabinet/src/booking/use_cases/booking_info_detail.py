from ..entities import BaseBookingCase
from ..repos import Booking, BookingRepo
from ..exceptions import BookingNotFoundError


class BookingDetailInfoCase(BaseBookingCase):
    """
    Инфо о бронированиях для МС лояльности.
    """

    def __init__(
        self,
        booking_repo: type[BookingRepo],
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()

    async def __call__(self, booking_amocrm_id: int) -> Booking:
        booking: Booking = await self.booking_repo.retrieve(
            filters=dict(amocrm_id=booking_amocrm_id),
            related_fields=[
                "property",
                "project",
                "project__city",
                "user",
            ],
        )
        if not booking:
            raise BookingNotFoundError

        return booking
