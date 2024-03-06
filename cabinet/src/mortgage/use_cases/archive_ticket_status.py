import structlog

from src.booking.repos import MortgageApplicationArchiveRepo
from src.mortgage.entities import BaseMortgageCase
from src.mortgage.event_emitter_handlers import mortage_event_emitter
from src.mortgage.models import ArchiveTicketStatusSchema


class ArchiveTicketStatusCase(BaseMortgageCase):
    def __init__(
        self,
        archive_repo: type[MortgageApplicationArchiveRepo],
    ):
        self.archive_repo: MortgageApplicationArchiveRepo = archive_repo()

        self.logger: structlog.BoundLogger = structlog.get_logger(self.__class__.__name__)

    async def __call__(self, payload: ArchiveTicketStatusSchema) -> None:
        data = payload.dict()
        is_created: bool = data.pop('is_created')
        self.logger.info('Сохранение статуса заявки на ипотеку в архив', data=data)
        mortgage_ticket_inform = await self.archive_repo.create(data=data)

        event = 'ticket_create' if is_created else 'ticket_change_status'
        mortage_event_emitter.ee.emit(
            event=event,
            booking_id=data["booking_id"],
            user=None,
            mortgage_ticket_inform=mortgage_ticket_inform,
        )
