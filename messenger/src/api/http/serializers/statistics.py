from pydantic import Field

from src.entities.statistics import TicketStatistics


class TicketsStatisticsResponse(TicketStatistics):
    returned_tickets_percent: float = Field(..., description="Percent of returned tickets, in range [0, 1]")
