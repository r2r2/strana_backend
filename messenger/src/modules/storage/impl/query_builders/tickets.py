from typing import Any

from sqlalchemy import nullslast, or_
from sqlalchemy.orm import aliased
from sqlalchemy.sql.selectable import Select

from src.api.http.serializers.tickets import TicketStatusFilter
from src.constants import INT32_MAX
from src.core.types import UserId
from src.entities.tickets import TicketFilters, TicketStatus
from src.entities.users import Language, Role
from src.modules.storage.models import Chat, Match, MatchScout, Sport, Ticket, User
from src.providers.i18n import get_localized_column

from .chats import ChatsQueryBuilder


class TicketsQueryBuilder:
    def __init__(self, user_id: UserId, user_role: Role | None) -> None:
        self.user_id = user_id
        self.user_role = user_role
        self.chat_qb = ChatsQueryBuilder(user_id, user_role=None)

    def build_base_query(self, lang: Language) -> Select[Any]:
        query = (
            self.chat_qb.build_base_query(apply_role_filter=False)
            .add_columns(
                # Ticket info
                Ticket.id.label("ticket_id"),
                Ticket.status,
                Ticket.created_from_chat_id.label("created_from_chat_id"),
                Ticket.created_at.label("ticket_created_at"),
                Ticket.updated_at.label("ticket_updated_at"),
                Ticket.comment,
                Ticket.close_reason,
                # Match info
                Match.sportlevel_id.label("match_id"),
                get_localized_column(Match, "team_a_name", lang).label("match_team_a_name"),
                get_localized_column(Match, "team_b_name", lang).label("match_team_b_name"),
                get_localized_column(Sport, "name", lang).label("match_sport_name"),
                Sport.id.label("match_sport_id"),
                Match.start_at.label("match_start_at"),
            )
            .join(Ticket, Ticket.chat_id == Chat.id)
            .outerjoin(Match, Chat.match_id == Match.sportlevel_id)
            .outerjoin(Sport, Match.sport_id == Sport.id)
            .order_by(None)
            .order_by(
                nullslast(self.chat_qb.messages_subq.c.id.desc()),
                Ticket.created_at.desc(),
            )
        )
        return self._apply_filter_by_role(query)

    def build_get_ticket_query(self, ticket_id: int, lang: Language) -> Select[Any]:
        return self.build_base_query(lang).where(Ticket.id == ticket_id)

    def build_ticket_list_query(
        self,
        status: TicketStatusFilter | None,
        lang: Language,
        filters: TicketFilters,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Select[Any]:
        query = self.build_base_query(lang)
        query = self._apply_filters(query, filters)

        if status:
            status_conditions = {
                TicketStatusFilter.NEW: Ticket.status == TicketStatus.NEW,
                TicketStatusFilter.IN_PROGRESS: Ticket.status == TicketStatus.IN_PROGRESS,
                TicketStatusFilter.SOLVED: or_(
                    Ticket.status == TicketStatus.SOLVED,
                    Ticket.status == TicketStatus.CONFIRMED,
                ),
            }
            query = query.where(status_conditions[status])

        return query.limit(limit).offset(offset)

    def _apply_filter_by_role(self, query: Select[Any]) -> Select[Any]:
        if not self.user_role:
            return query

        match self.user_role:
            case Role.SUPERVISOR:
                return query
            case _:
                return query.where(Ticket.created_by == self.user_id)

    def _apply_filters(self, query: Select[Any], filters: TicketFilters) -> Select[Any]:
        if filters.assigned_to_me:
            query = query.where(Ticket.assigned_to_user_id == self.user_id)

        if filters.match_id:
            query = query.where(Match.sportlevel_id == filters.match_id)

        if filters.search_query:
            query = self._apply_smart_search_filter(query=query, search_string=filters.search_query)

        if filters.scout_numbers:
            query = query.join(MatchScout, MatchScout.sportlevel_match_id == Match.sportlevel_id).where(
                MatchScout.scout_number.in_(filters.scout_numbers),
            )

        if filters.sport_ids:
            query = query.where(Match.sport_id.in_(filters.sport_ids))

        if filters.ticket_date_from:
            query = query.where(Ticket.created_at >= filters.ticket_date_from)

        if filters.ticket_date_to:
            query = query.where(Ticket.created_at < filters.ticket_date_to)

        if filters.match_date_from:
            query = query.where(Match.start_at >= filters.match_date_from)

        if filters.match_date_to:
            query = query.where(Match.start_at < filters.match_date_to)

        return query  # noqa: RET504

    def _apply_smart_search_filter(
        self,
        query: Select[Any],
        search_string: str,
    ) -> Select[Any]:
        search_string = search_string.lower()

        if search_string.isdigit() and search_string.isascii():
            search_val = int(search_string)
            if search_val >= INT32_MAX:
                return query

            created_by_user = aliased(User, name="created_by_user")

            # Filter by match id, ticket author id, ticket author scout number
            return query.outerjoin(created_by_user, Ticket.created_by == created_by_user.sportlevel_id).where(
                or_(
                    Ticket.id == search_val,
                    Ticket.created_by == search_val,
                    Ticket.assigned_to_user_id == search_val,
                    Match.sportlevel_id == search_val,
                    created_by_user.scout_number == search_val,
                ),
            )

        return query
