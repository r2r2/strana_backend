from typing import Any

from sqlalchemy import Select, and_, func, or_, select
from sqlalchemy import true as sqla_true
from sqlalchemy.sql.selectable import LateralFromClause

from src.core.types import UserId
from src.entities.matches import ChatType
from src.modules.storage.models import Chat, ChatMembership, Match, Message


class UnreadCountersQueryBuilder:
    def __init__(self, user_id: UserId) -> None:
        self.user_id = user_id

        self.unread_by_chat_lateral = self._build_chat_unread_count_lateral()
        self.unread_by_match_lateral = self._build_match_unread_count_lateral()

    def build_total_unread_count_query(self, chat_type: ChatType | None) -> Select[tuple[int]]:
        query = (
            select(func.sum(self.unread_by_chat_lateral.c.count))
            .select_from(Chat)
            .join(ChatMembership, and_(ChatMembership.chat_id == Chat.id, ChatMembership.user_id == self.user_id))
            .join(self.unread_by_chat_lateral, sqla_true())
        )

        match chat_type:
            case ChatType.PERSONAL | ChatType.TICKET:
                query = query.where(Chat.type == chat_type)
            case ChatType.MATCH:
                query = query.where(Chat.match_id.isnot(None))
            case None:
                ...

        return query

    def build_unread_count_by_chat_query(self, chat_id: int) -> Select[tuple[int]]:
        return (
            select(self.unread_by_chat_lateral.c.count.label("unread_count"))
            .select_from(Chat)
            .join(ChatMembership, and_(ChatMembership.chat_id == Chat.id, ChatMembership.user_id == self.user_id))
            .join(self.unread_by_chat_lateral, sqla_true())
            .where(Chat.id == chat_id)
        )

    def build_unread_count_by_chats_query(self, chat_ids: list[int]) -> Select[tuple[int, int]]:
        return (
            select(self.unread_by_chat_lateral.c.count.label("unread_count"), Chat.id.label("chat_id"))
            .select_from(Chat)
            .join(ChatMembership, and_(ChatMembership.chat_id == Chat.id, ChatMembership.user_id == self.user_id))
            .join(self.unread_by_chat_lateral, sqla_true())
            .where(Chat.id.in_(chat_ids))
        )

    def build_unread_count_by_match_query(self, match_id: int) -> Select[tuple[int]]:
        return (
            select(self.unread_by_match_lateral.c.unread_count.label("unread_count"))
            .select_from(Match)
            .join(Chat, Chat.match_id == Match.sportlevel_id)
            .join(ChatMembership, and_(ChatMembership.chat_id == Chat.id, ChatMembership.user_id == self.user_id))
            .join(self.unread_by_match_lateral, sqla_true())
            .where(Match.sportlevel_id == match_id)
        )

    def build_unread_count_by_matches_query(self, match_ids: list[int]) -> Select[tuple[int, int]]:
        return (  # type: ignore
            select(
                self.unread_by_match_lateral.c.unread_count.label("unread_count"),
                Chat.match_id.label("match_id"),
            )
            .select_from(Match)
            .join(Chat, Chat.match_id == Match.sportlevel_id)
            .join(ChatMembership, and_(ChatMembership.chat_id == Chat.id, ChatMembership.user_id == self.user_id))
            .join(self.unread_by_match_lateral, sqla_true())
            .where(Match.sportlevel_id.in_(match_ids))
        )

    def _build_chat_unread_count_lateral(self) -> LateralFromClause[int]:
        """Subquery - count unread messages for chat, uses Chat.id, ChatMembership.last_read_message_id"""
        return (
            select(
                func.count(Message.id).label("count"),
            )
            .select_from(Message)
            .where(
                or_(
                    Message.sender_id != self.user_id,
                    Message.sender_id.is_(None),
                ),
                Message.chat_id == Chat.id,
                Message.id > ChatMembership.last_read_message_id,
            )
            .correlate(Chat, ChatMembership)
            .lateral("chat_unread_single_subq")
        )

    def _build_match_unread_count_lateral(self) -> LateralFromClause[Any]:
        """Generates subquery that selects unread count for match, lateral to Match"""
        chat_unread_single_subq = self._build_chat_unread_count_lateral()

        return (
            select(
                func.sum(chat_unread_single_subq.c.count).label("unread_count"),
            )
            .select_from(Chat)
            .join(ChatMembership, and_(Chat.id == ChatMembership.chat_id, ChatMembership.user_id == self.user_id))
            .join(chat_unread_single_subq, sqla_true())
            .where(Chat.match_id == Match.sportlevel_id)
            .group_by(Chat.match_id)
            .correlate(Match)
            .lateral("match_unread_subq")
        )
