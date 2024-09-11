from datetime import datetime

from sqlalchemy import RowMapping, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.http.serializers.chats import ChatResponse
from src.api.http.serializers.tickets import TicketInfo, TicketMatchInfo, TicketStatusFilter
from src.core.common.utility import pick_fields
from src.core.types import UserId
from src.entities.chats import ChatMemberInfo
from src.entities.tickets import TicketCloseReason, TicketFilters, TicketStatus
from src.entities.users import Language, Role
from src.modules.storage.impl.query_builders import TicketsQueryBuilder
from src.modules.storage.impl.query_builders.common import get_count
from src.modules.storage.interface import TicketOperationsProtocol
from src.modules.storage.models import Chat, Ticket, TicketStatusLog
from src.providers.i18n import parse_message_content
from src.providers.time import datetime_now


class TicketOperations(TicketOperationsProtocol):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _compose_result(self, row: RowMapping) -> TicketInfo:
        last_message_id = row.last_message_id
        last_message_content = row.last_message_content
        last_message_created_at = row.last_message_created_at
        last_message_sender_id = row.last_message_sender_id
        if row.first_message_id == row.last_message_id:
            # Если сообщение в заявке единственное, то не нужно возвращать последнее.
            last_message_id = None
            last_message_content = None
            last_message_created_at = None
            last_message_sender_id = None

        return TicketInfo(
            **pick_fields(
                row,
                include={
                    "ticket_id",
                    "status",
                    "created_from_chat_id",
                    "comment",
                    "close_reason",
                    "ticket_created_at",
                    "ticket_updated_at",
                },
            ),
            match_info=TicketMatchInfo(
                id=row.match_id,
                team_a_name=row.match_team_a_name,
                team_b_name=row.match_team_b_name,
                sport_name=row.match_sport_name,
                sport_id=row.match_sport_id,
                start_at=row.match_start_at,
            ),
            chat_info=ChatResponse(
                unread_count=0,
                chat_id=row.chat_id,
                type=row.type,
                is_member=row.is_member,
                match_id=row.match_id,
                last_message_id=last_message_id,
                last_message_content=parse_message_content(last_message_content),
                last_message_sender_id=last_message_sender_id,
                last_message_created_at=last_message_created_at,
                first_message_id=row.first_message_id,
                first_message_content=parse_message_content(row.first_message_content),
                first_message_sender_id=row.first_message_sender_id,
                first_message_created_at=row.first_message_created_at,
                has_write_permission=row.has_write_permission,
                last_read_message_id=row.last_read_message_id,
                last_unread_message_id=row.last_unread_message_id,
                meta=row.meta,
                is_closed=row.is_closed,
                members=[
                    ChatMemberInfo(
                        user_id=entry["user_id"],
                        is_primary_member=entry["is_primary_member"],
                        is_online=False,
                        user_role=entry["user_role"],
                    )
                    for entry in row.members
                ],
            ),
        )

    async def search_tickets(
        self,
        user_id: UserId,
        user_role: Role,
        status: TicketStatusFilter | None,
        lang: Language,
        filters: TicketFilters,
        limit: int | None = None,
        offset: int | None = None,
    ) -> tuple[list[TicketInfo], int]:
        query_builder = TicketsQueryBuilder(user_id=user_id, user_role=user_role)
        query = query_builder.build_ticket_list_query(
            status=status,
            lang=lang,
            filters=filters,
            limit=limit,
            offset=offset,
        )
        total = await get_count(query, self.session)
        result = await self.session.execute(query)
        return [self._compose_result(row) for row in result.mappings().fetchall()], total

    async def get_ticket_by_id(self, ticket_id: int) -> Ticket | None:
        query = select(Ticket).where(Ticket.id == ticket_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_ticket_by_chat_id(self, chat_id: int) -> Ticket | None:
        query = select(Ticket).where(Ticket.created_from_chat_id == chat_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_ticket(
        self,
        created_by: UserId,
        created_from_chat_id: int | None,
        chat_id: int,
    ) -> Ticket:
        ticket = Ticket(
            created_by=created_by,
            created_from_chat_id=created_from_chat_id,
            chat_id=chat_id,
            status=TicketStatus.NEW,
            assigned_to_user_id=None,
            comment=None,
            close_reason=None,
            created_at=datetime_now(),
            updated_at=None,
        )
        self.session.add(ticket)
        await self.session.flush()

        return ticket

    async def update_ticket_status(self, ticket: Ticket, new_status: TicketStatus, updated_by: int) -> bool:
        last_status_updated_at = ticket.updated_at or ticket.created_at
        old_status = ticket.status

        update_q = (
            update(Ticket)
            .values(status=new_status, updated_at=datetime_now())
            .where(Ticket.id == ticket.id)
            .returning(Ticket.id)
        )
        result = await self.session.execute(update_q)
        if not result.scalar_one_or_none():
            return False

        await self._save_ticket_status_log(
            ticket_id=ticket.id,
            old_status=old_status,
            new_status=new_status,
            updated_by=updated_by,
            last_status_updated_at=last_status_updated_at,
        )

        return True

    async def close_ticket(
        self,
        ticket: Ticket,
        comment: str,
        reason: TicketCloseReason,
        updated_by: UserId,
    ) -> None:
        last_status_updated_at = ticket.updated_at or ticket.created_at
        old_status = ticket.status

        update_q = (
            update(Ticket)
            .values(
                status=TicketStatus.SOLVED,
                comment=comment,
                close_reason=reason,
                updated_at=datetime_now(),
            )
            .where(Ticket.id == ticket.id)
        )
        await self.session.execute(update_q)
        await self._save_ticket_status_log(
            ticket_id=ticket.id,
            old_status=old_status,
            new_status=TicketStatus.SOLVED,
            updated_by=updated_by,
            last_status_updated_at=last_status_updated_at,
        )

    async def get_ticket_detailed(
        self,
        user_id: UserId,
        user_role: Role,
        lang: Language,
        ticket_id: int,
    ) -> TicketInfo | None:
        query_builder = TicketsQueryBuilder(user_id=user_id, user_role=user_role)
        query = query_builder.build_get_ticket_query(ticket_id=ticket_id, lang=lang)
        result = await self.session.execute(query)
        row = result.mappings().one_or_none()
        if not row:
            return None

        return self._compose_result(row)

    async def assign_to_user(self, ticket_id: int, user_id: int) -> None:
        update_q = (
            update(Ticket)
            .values(
                assigned_to_user_id=user_id,
            )
            .where(Ticket.id == ticket_id)
        )
        await self.session.execute(update_q)

    async def _save_ticket_status_log(
        self,
        ticket_id: int,
        old_status: TicketStatus,
        new_status: TicketStatus,
        updated_by: UserId,
        last_status_updated_at: datetime,
    ) -> TicketStatusLog:
        now = datetime_now()
        time_after_last_status = now - last_status_updated_at

        status_log = TicketStatusLog(
            ticket_id=ticket_id,
            old_status=old_status,
            new_status=new_status,
            updated_by=updated_by,
            created_at=now,
            time_after_last_status=int(time_after_last_status.total_seconds()),
        )
        self.session.add(status_log)
        await self.session.flush()
        return status_log

    async def count_tickets(
        self,
        status: TicketStatus,
        assigned_to_user_id: int | None = None,
    ) -> int:
        query = select(func.count(Ticket.id)).where(Ticket.status == status)
        if assigned_to_user_id:
            query = query.where(Ticket.assigned_to_user_id == assigned_to_user_id)

        result = await self.session.execute(query)
        return result.scalar_one()

    async def check_user_ticket(self, user_id: int, match_id: int, chat_id: int) -> bool:
        query = (
            select(Ticket.id)
            .select_from(Ticket)
            .join(Chat, Ticket.chat_id == Chat.id)
            .where(
                Ticket.created_by == user_id,
                Ticket.chat_id == chat_id,
                Chat.match_id == match_id,
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None
