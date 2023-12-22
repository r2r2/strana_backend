import asyncio

import structlog

from src.booking.repos import BookingRepo, Booking
from src.mortgage.entities import BaseMortgageService
from src.mortgage.exceptions import MortgageTicketNotFoundError, MortgageApplicationStatusNotFoundError
from src.mortgage.repos import (
    MortgageApplicationStatusRepo,
    MortgageDeveloperTicketRepo,
    MortgageDeveloperTicket,
    MortgageApplicationStatus,
)


class ChangeMortgageTicketStatusService(BaseMortgageService):
    """
    Сервис изменения статуса заявки на ипотеку.
    """

    def __init__(
        self,
        mortgage_application_status_repo: type[MortgageApplicationStatusRepo],
        mortgage_dev_ticket_repo: type[MortgageDeveloperTicketRepo],
        booking_repo: type[BookingRepo],
    ):
        self.mortgage_application_status_repo: MortgageApplicationStatusRepo = mortgage_application_status_repo()
        self.mortgage_dev_ticket_repo: MortgageDeveloperTicketRepo = mortgage_dev_ticket_repo()
        self.booking_repo: BookingRepo = booking_repo()

        self.logger: structlog.BoundLogger = structlog.get_logger(self.__class__.__name__)

    async def __call__(self, booking_id: int) -> None:
        """
        Изменение статуса заявки на ипотеку.
        """
        self.logger.info(f"Start changing mortgage ticket status {booking_id=}")
        booking: Booking = await self.booking_repo.retrieve(
            filters=dict(id=booking_id),
            related_fields=["amocrm_status"],
        )
        ticket: MortgageDeveloperTicket = await self.mortgage_dev_ticket_repo.retrieve(
            filters=dict(booking=booking),
        )
        if not ticket:
            self.logger.info(f'MortgageDeveloperTicket not found. {booking_id=}')
            raise MortgageTicketNotFoundError

        status: MortgageApplicationStatus = await self.mortgage_application_status_repo.retrieve(
            filters=dict(amocrm_statuses__in=[booking.amocrm_status]),
        )
        if not status:
            self.logger.info(f'MortgageApplicationStatus not found. {booking_id=}')
            raise MortgageApplicationStatusNotFoundError

        await self.mortgage_dev_ticket_repo.update(
            model=ticket,
            data=dict(status=status),
        )
        self.logger.info(
            f"Finish changing mortgage ticket status: {booking_id=}; {status=}; {ticket}."
        )

    def as_task(self, booking_id: int) -> asyncio.Task:
        """
        Запуск сервиса в виде таски.
        """
        return asyncio.create_task(self(booking_id=booking_id))
