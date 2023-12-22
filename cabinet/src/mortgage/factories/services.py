from src.booking.repos import BookingRepo
from src.mortgage.repos import MortgageDeveloperTicketRepo, MortgageApplicationStatusRepo
from src.mortgage.services import ChangeMortgageTicketStatusService


class ChangeMortgageTicketStatusServiceFactory:
    @staticmethod
    def create():
        return ChangeMortgageTicketStatusService(
            mortgage_application_status_repo=MortgageApplicationStatusRepo,
            mortgage_dev_ticket_repo=MortgageDeveloperTicketRepo,
            booking_repo=BookingRepo,
        )
