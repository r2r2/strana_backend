from typing import Any

from sqlalchemy import exists, func, literal, nullslast, or_, select
from sqlalchemy import true as sqla_true
from sqlalchemy.sql.selectable import Select

from src.constants import INT32_MAX
from src.core.types import UserId
from src.entities.matches import ChatType, MatchFilters
from src.entities.users import Language, Role
from src.modules.storage.models import Chat, ChatMembership, Match, MatchScout, Sport
from src.modules.storage.models.user import User
from src.providers.i18n import get_localized_column

from .chats import ChatsQueryBuilder

match_scouts_lateral = (
    select(
        func.array_agg(
            func.jsonb_build_object(
                literal("scout_number"),
                MatchScout.scout_number,
                literal("is_main_scout"),
                MatchScout.is_main_scout,
                literal("name"),
                User.name,
                literal("id"),
                User.sportlevel_id,
            ),
        ).label("scouts"),
    )
    .select_from(MatchScout)
    .join(User, MatchScout.scout_number == User.scout_number)
    .where(MatchScout.sportlevel_match_id == Match.sportlevel_id)
    .correlate(Match)
    .lateral("scouts_subq")
)


class MatchesQueryBuilder:
    def __init__(self, user_id: UserId, user_role: Role, lang: Language, chat_type: ChatType | None = None) -> None:
        self.lang = lang
        self.user_id = user_id
        self.user_role = user_role
        self.chat_list_qb = ChatsQueryBuilder(user_id, user_role)
        self.last_messages_subq = (
            self.chat_list_qb.build_get_chat_list_query(
                show_chats_for_tickets=True,
                exclude_non_member_chats=True,
                chat_type=chat_type,
            )
            .where(Chat.match_id == Match.sportlevel_id)
            .limit(1)
            .correlate(Match)
            .lateral("last_messages_subq")
        )

    @classmethod
    def build_get_match_basic_info(cls, sportlevel_id: int) -> Select[Any]:
        return (
            select(
                Match,
                func.coalesce(match_scouts_lateral.c.scouts, []).label("scouts"),
            )
            .select_from(Match)
            .outerjoin(match_scouts_lateral, sqla_true())
            .where(Match.sportlevel_id == sportlevel_id)
        )

    def build_get_match_list_query(self, filters: MatchFilters, limit: int, offset: int) -> Select[Any]:
        """Generates query that selects all matches with pagination"""
        query = self._build_base_query()

        if filters.search_query:
            match self.user_role:
                case Role.SCOUT:
                    # Match should be accessible to scout if any:
                    # 1. Scout is a member of any chat within the match
                    # 2. Scout is in scouts list of the match
                    match_scouts_check_lat = (
                        select(MatchScout.id.label("scout_link_id"))
                        .select_from(MatchScout)
                        .join(User, User.scout_number == MatchScout.scout_number)
                        .where(
                            User.sportlevel_id == self.user_id,
                            MatchScout.sportlevel_match_id == Match.sportlevel_id,
                        )
                        .correlate(Match)
                        .lateral("scout_numbers_lateral")
                    )

                    query = query.outerjoin(match_scouts_check_lat, sqla_true()).where(
                        or_(
                            match_scouts_check_lat.c.scout_link_id.isnot(None),
                            self.last_messages_subq.c.last_message_id.isnot(None),
                        ),
                    )

                case _:
                    ...

            query = self._apply_smart_search_filter(
                query=query,
                search_string=filters.search_query,
                filter_by_scout_numbers=self.user_role != Role.SCOUT,
            )

        else:
            query = query.where(self.last_messages_subq.c.last_message_id.isnot(None))

        query = self._apply_filters(query, filters)

        return query.limit(limit).offset(offset)

    def _apply_filters(self, query: Select[Any], filters: MatchFilters) -> Select[Any]:
        if filters.scout_numbers:
            query = query.join(MatchScout, MatchScout.sportlevel_match_id == Match.sportlevel_id).where(
                MatchScout.scout_number.in_(filters.scout_numbers),
            )

        if filters.sport_ids:
            query = query.where(Match.sport_id.in_(filters.sport_ids))

        if filters.match_date_from:
            query = query.where(Match.start_at >= filters.match_date_from)

        if filters.match_date_to:
            query = query.where(Match.start_at < filters.match_date_to)

        if filters.state:
            query = query.where(Match.state == filters.state)

        return query

    def build_get_match_list_short_info(self, filters: MatchFilters, limit: int, offset: int) -> Select[Any]:
        query = self._build_short_base_query()
        match self.user_role:
            case Role.BOOKMAKER | Role.SCOUT:
                # Bookmaker&Scout can access only matches, available to him.
                chat_member_query = (
                    select(Match.sportlevel_id)
                    .select_from(Match)
                    .join(Chat, Chat.match_id == Match.sportlevel_id)
                    .join(ChatMembership, ChatMembership.chat_id == Chat.id)
                    .where(ChatMembership.user_id == self.user_id)
                )
                query = query.where(Match.sportlevel_id.in_(chat_member_query))
            case _:
                ...

        if filters.search_query:
            query = self._apply_smart_search_filter(
                query=query,
                search_string=filters.search_query,
                filter_by_scout_numbers=self.user_role != Role.SCOUT,
            )

        query = self._apply_filters(query, filters)
        return query.limit(limit).offset(offset)

    def build_get_match_query(self, match_id: int) -> Select[Any]:
        """Generates query that selects the specified match"""
        return self._build_base_query().where(Match.sportlevel_id == match_id)

    def _apply_smart_search_filter(
        self,
        query: Select[Any],
        search_string: str,
        filter_by_scout_numbers: bool,
    ) -> Select[Any]:
        search_string = search_string.lower()

        if search_string.isdigit() and search_string.isascii():
            search_val = int(search_string)
            if search_val >= INT32_MAX:
                return query

            if filter_by_scout_numbers:
                match_scout_select_lat = (
                    select(MatchScout.scout_number)
                    .select_from(MatchScout)
                    .where(MatchScout.scout_number == search_val)
                    .where(MatchScout.sportlevel_match_id == Match.sportlevel_id)
                    .correlate(Match)
                    .limit(1)
                    .lateral("match_scouts_array_lateral")
                )

                # Filter by match id and scout number
                query = query.outerjoin(match_scout_select_lat, sqla_true()).where(
                    or_(
                        Match.sportlevel_id == search_val,
                        exists(match_scout_select_lat.c.scout_number),
                    ),
                )

            # Filter by match id
            return query.where(Match.sportlevel_id == search_val)

        # Filter by match team names
        return query.where(
            or_(
                func.lower(get_localized_column(Match, "team_a_name", self.lang)).contains(search_string),
                func.lower(get_localized_column(Match, "team_b_name", self.lang)).contains(search_string),
            ),
        )

    def _build_base_query(self) -> Select[Any]:
        """Generates query that selects all matches"""
        return (
            select(
                Match.sportlevel_id,
                Match.sport_id,
                Match.start_at,
                Match.state,
                get_localized_column(Match, "team_a_name", self.lang).label("team_a_name"),
                get_localized_column(Match, "team_b_name", self.lang).label("team_b_name"),
                get_localized_column(Sport, "name", self.lang).label("sport_name"),
                self.last_messages_subq.c.last_message_id,
                self.last_messages_subq.c.last_message_created_at,
                self.last_messages_subq.c.last_message_content,
                self.last_messages_subq.c.last_message_sender_id,
                self.last_messages_subq.c.chat_id,
            )
            .select_from(Match)
            .outerjoin(self.last_messages_subq, sqla_true())
            .join(Sport, Match.sport_id == Sport.id)
            .order_by(nullslast(self.last_messages_subq.c.last_message_id.desc()))  # TODO: [high] slow condition
        )

    def _build_short_base_query(self) -> Select[Any]:
        return (
            select(
                Match.sportlevel_id,
                Match.sport_id,
                Match.start_at,
                Match.state,
                get_localized_column(Match, "team_a_name", self.lang).label("team_a_name"),
                get_localized_column(Match, "team_b_name", self.lang).label("team_b_name"),
                get_localized_column(Sport, "name", self.lang).label("sport_name"),
            )
            .select_from(Match)
            .join(Sport, Match.sport_id == Sport.id)
            .order_by(Match.start_at.desc())
        )
