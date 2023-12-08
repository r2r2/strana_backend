from src.booking.repos import BookingRepo, Booking
from src.mortgage_calculator.entities import BaseMortgageCase
from src.mortgage_calculator.services import MortgageTicketCheckerService


class GetMortgageBookingsCase(BaseMortgageCase):
    def __init__(
        self,
        booking_repo: type[BookingRepo],
        ticket_checker_service: type[MortgageTicketCheckerService],
    ):
        self.booking_repo: BookingRepo = booking_repo()
        self.ticket_checker_service: type[MortgageTicketCheckerService] = ticket_checker_service

    async def __call__(self, user_id: int) -> list[Booking]:
        bookings: list[Booking | None] = await self._get_bookings(user_id=user_id)
        filtered_bookings: list[Booking] = []
        for booking in bookings:
            is_booking_in_matrix, is_eligible_for_mortgage = await self.ticket_checker_service(booking).check()
            if is_booking_in_matrix:
                booking.is_eligible_for_mortgage = is_eligible_for_mortgage
                filtered_bookings.append(booking)
        return filtered_bookings

    async def _get_bookings(self, user_id: int) -> list[Booking | None]:
        filters: dict = dict(
            active=True,
            user_id=user_id,
            property_id__isnull=False,
            property__property_type__is_active=True,
            building_id__isnull=False,
            project_id__isnull=False,
        )
        related_fields = [
            "property__section",
            "property__property_type",
            "floor",
            "building",
            "project",
            "ddu",
            "agent",
            "agency",
            "booking_source",
        ]
        bookings: list[Booking] = await self.booking_repo.list(
            filters=filters,
            related_fields=related_fields,
        )
        return bookings
