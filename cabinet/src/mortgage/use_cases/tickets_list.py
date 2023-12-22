import asyncio
from typing import Any

from src.booking.repos import BookingRepo, Booking
from src.mortgage.entities import BaseMortgageCase
from src.mortgage.repos import (
    MortgageDeveloperTicketRepo,
    MortgageDeveloperTicket,
    MortgageApplicationStatusRepo,
    MortgageOfferRepo,
    MortgageApplicationStatus,
)


class GetMortgageTicketListCase(BaseMortgageCase):
    def __init__(
        self,
        booking_repo: type[BookingRepo],
        mortgage_dev_ticket_repo: type[MortgageDeveloperTicketRepo],
        mortgage_status_repo: type[MortgageApplicationStatusRepo],
        mortgage_offer_repo: type[MortgageOfferRepo],
    ):
        self.booking_repo: BookingRepo = booking_repo()
        self.mortgage_dev_ticket_repo: MortgageDeveloperTicketRepo = mortgage_dev_ticket_repo()
        self.mortgage_status_repo: MortgageApplicationStatusRepo = mortgage_status_repo()
        self.mortgage_offer_repo: MortgageOfferRepo = mortgage_offer_repo()

    async def __call__(self, user_id: int) -> dict[str, Any]:
        bookings: list[Booking] = await self.booking_repo.list(
            filters=dict(user_id=user_id),
            related_fields=["amocrm_status"],
        )

        async_db_queries = [
            self._get_tickets(booking=booking)
            for booking in bookings
        ]
        tickets: list[MortgageDeveloperTicket | None] = []
        for ticket in await asyncio.gather(*async_db_queries):
            if ticket:
                tickets += ticket

        statuses: list[MortgageApplicationStatus] = await self.mortgage_status_repo.list(ordering="priority")
        return dict(
            statuses=statuses,
            tickets=tickets,
        )

    async def _get_tickets(self, booking: Booking) -> list[MortgageDeveloperTicket | None]:
        tickets: list[MortgageDeveloperTicket | None] = await self.mortgage_dev_ticket_repo.list(
            filters=dict(booking=booking),
            annotations=dict(
                rate=self.mortgage_offer_repo.a_builder.build_min("offers__percent_rate"),
            ),
            prefetch_fields=[
                "status",
                "calculator_condition",
            ],
        )
        return tickets
