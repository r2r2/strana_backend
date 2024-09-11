from datetime import datetime

from sqlalchemy import distinct, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.statistics import TicketStatistics
from src.entities.tickets import TicketStatus
from src.exceptions import InternalError
from src.modules.storage.interface import StatsOperationsProtocol
from src.modules.storage.models import Ticket, TicketStatusLog


class StatisticsOperations(StatsOperationsProtocol):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_ticket_stats(
        self,
        for_user: int | None,
        date_from: datetime,
        date_to: datetime,
    ) -> TicketStatistics:
        query = (
            select(
                (
                    func.count(distinct(Ticket.id))
                    .filter(
                        or_(
                            TicketStatusLog.new_status == TicketStatus.CONFIRMED,
                            TicketStatusLog.new_status == TicketStatus.SOLVED,
                        )
                    )
                    .label("solved_tickets_count")
                ),
                (
                    func.count()
                    .filter(
                        TicketStatusLog.new_status == TicketStatus.IN_PROGRESS,
                        TicketStatusLog.old_status == TicketStatus.SOLVED,
                    )
                    .label("returned_tickets_count")
                ),
                func.coalesce(
                    func.avg(TicketStatusLog.time_after_last_status).filter(
                        TicketStatusLog.new_status == TicketStatus.IN_PROGRESS,
                        TicketStatusLog.old_status == TicketStatus.NEW,
                    ),
                    0,
                ).label("avg_time_to_first_response"),
                func.coalesce(
                    func.avg(TicketStatusLog.time_after_last_status).filter(
                        TicketStatusLog.new_status == TicketStatus.SOLVED,
                    ),
                    0,
                ).label("avg_time_to_solve"),
            )
            .select_from(Ticket)
            .join(TicketStatusLog, TicketStatusLog.ticket_id == Ticket.id)
            .where(
                TicketStatusLog.created_at >= date_from,
                TicketStatusLog.created_at < date_to,
            )
        )
        if for_user:
            query = query.filter(Ticket.assigned_to_user_id == for_user)

        result = await self.session.execute(query)
        if not (first := result.mappings().fetchone()):
            raise InternalError("Invalid SQL query result")

        return TicketStatistics(
            solved_tickets_count=first["solved_tickets_count"],
            returned_tickets_count=first["returned_tickets_count"],
            avg_time_to_first_response=int(first["avg_time_to_first_response"]),
            avg_time_to_solve=int(first["avg_time_to_solve"]),
        )
