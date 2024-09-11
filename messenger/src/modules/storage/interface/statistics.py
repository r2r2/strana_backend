from datetime import datetime
from typing import Protocol

from src.entities.statistics import TicketStatistics


class StatsOperationsProtocol(Protocol):
    async def get_ticket_stats(
        self,
        for_user: int | None,
        date_from: datetime,
        date_to: datetime,
    ) -> TicketStatistics: ...
