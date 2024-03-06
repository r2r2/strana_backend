from src.booking.repos import BookingRepo
from src.mortgage.entities import BaseMortgageCase


class GetBookingsAgentsCase(BaseMortgageCase):
    def __init__(
        self,
        booking_repo: type[BookingRepo],
    ):
        self.booking_repo: BookingRepo = booking_repo()

    async def __call__(self, user_id: int) -> list[dict]:
        query_fields: list[str] = [
            "id",
            "amocrm_id",
            "active",
            "amocrm_status_id",
            "agent_id",
            "agent__name",
            "agent__surname",
            "agent__patronymic",
            "agent__phone",
            "agent__email",
            "agent__amocrm_id",
            "building__name",
            "property__rooms",
            "property__number",
            "property__area",
            "property__price",
            "property__plan",
            "floor__number",
            "project__name",
            "user_id",
            "property__property_type__is_active",
        ]
        bookings: list[dict] = await self.booking_repo.list(
            filters=dict(amocrm_id__isnull=False, user_id=user_id),
        ).values(*query_fields)

        return bookings
