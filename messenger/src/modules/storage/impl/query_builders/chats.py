from typing import Any

from sqlalchemy import and_, func, nullslast, or_, select
from sqlalchemy import text as sqla_text
from sqlalchemy import true as sqla_true
from sqlalchemy.sql import ColumnElement
from sqlalchemy.sql.selectable import LateralFromClause, Select

from src.core.types import UserId
from src.entities.matches import ChatType
from src.entities.users import Role
from src.modules.storage.models import Chat, ChatMembership, Message


class ChatsQueryBuilder:
    def __init__(self, user_id: UserId, user_role: Role | None) -> None:
        self.user_id = user_id
        self.user_role = user_role

        self.messages_subq = self._build_last_messages_subquery()
        self.first_messages_subq = self._build_first_messages_subquery()
        self.chat_members_subq = self._build_chat_members_subquery()
        self.last_unread_message_subq = self._build_last_unread_message_subquery()

    def build_base_query(
        self,
        apply_role_filter: bool = True,
        show_chats_for_tickets: bool = False,
        exclude_non_member_chats: bool = False,
    ) -> Select[Any]:
        query = (
            select(
                Chat.match_id,
                Chat.type,
                Chat.id.label("chat_id"),
                Chat.meta,
                Chat.is_closed,
                self.messages_subq.c.id.label("last_message_id"),
                self.messages_subq.c.content.label("last_message_content"),
                self.messages_subq.c.sender_id.label("last_message_sender_id"),
                self.messages_subq.c.created_at.label("last_message_created_at"),
                self.last_unread_message_subq.c.id.label("last_unread_message_id"),
                self.first_messages_subq.c.id.label("first_message_id"),
                self.first_messages_subq.c.content.label("first_message_content"),
                self.first_messages_subq.c.sender_id.label("first_message_sender_id"),
                self.first_messages_subq.c.created_at.label("first_message_created_at"),
                func.coalesce(ChatMembership.last_read_message_id, 0).label("last_read_message_id"),
                func.coalesce(ChatMembership.has_write_permission, False).label("has_write_permission"),
                (ChatMembership.id.isnot(None)).label("is_member"),
                self.chat_members_subq.c.members.label("members"),
            )
            .select_from(Chat)
            .outerjoin(ChatMembership, and_(Chat.id == ChatMembership.chat_id, ChatMembership.user_id == self.user_id))
            .outerjoin(self.messages_subq, sqla_true())
            .outerjoin(self.last_unread_message_subq, sqla_true())
            .outerjoin(self.first_messages_subq, sqla_true())
            .join(self.chat_members_subq, sqla_true())
            .order_by(nullslast(self.messages_subq.c.id.desc()))
        )

        if exclude_non_member_chats:
            return query.where(ChatMembership.id.isnot(None))

        if apply_role_filter:
            return query.where(self.make_filter_by_role(show_chats_for_tickets))

        return query

    def build_get_chat_list_query(
        self,
        match_id: int | None = None,
        chat_type: ChatType | None = None,
        show_chats_for_tickets: bool = False,
        exclude_non_member_chats: bool = False,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Select[Any]:
        """Generates a query that selects all chats"""
        query = self.build_base_query(
            show_chats_for_tickets=show_chats_for_tickets,
            exclude_non_member_chats=exclude_non_member_chats,
        ).order_by(
            self.messages_subq.c.id.desc(),
        )

        if match_id:
            query = query.where(Chat.match_id == match_id)

        if chat_type is not None:
            query = query.where(Chat.type == chat_type)

            if chat_type == ChatType.PERSONAL:
                query = query.where(ChatMembership.id.isnot(None))

        return query.limit(limit).offset(offset)

    def build_get_chat_query(self, chat_id: int) -> Select[Any]:
        """Generates query that selects single chat by ID"""
        return self.build_base_query(
            show_chats_for_tickets=True,
            exclude_non_member_chats=False,
        ).where(Chat.id == chat_id)

    def make_filter_by_role(self, show_chats_for_tickets: bool = False) -> ColumnElement[bool]:
        # User with any role has access to read the chat room of which he is a member
        conditions: list[ColumnElement[Any]] = [ChatMembership.id.isnot(None)]

        match self.user_role:
            case None | Role.SCOUT:
                # Scout can access only his own chats.
                # If no role is specified, filter only by chats in which the user is a member
                ...

            case Role.BOOKMAKER | Role.SUPERVISOR:
                # Bookmaker, Supervisor and admin have access to other bookmakers' chats with the scout
                conditions.append(Chat.type == ChatType.MATCH)

            case _:
                raise RuntimeError(f"Unknown user role: {self.user_role}")

        if not show_chats_for_tickets:
            return and_(
                and_(
                    # Users should not see ticket chats in chat list
                    Chat.type != ChatType.TICKET,
                ),
                or_(*conditions),
            )

        return or_(*conditions)

    def _build_last_unread_message_subquery(self) -> LateralFromClause:
        """Subquery - last unread message for chat, lateral to ChatMembership"""
        return (
            select(Message.id)
            .select_from(Message)
            .where(
                Message.id > func.coalesce(ChatMembership.last_read_message_id, 0),
                Message.sender_id != self.user_id,
                Message.chat_id == ChatMembership.chat_id,
            )
            .order_by(Message.id)
            .limit(1)
            .correlate(ChatMembership)
            .lateral("last_unread_messages_subq")
        )

    def _build_last_messages_subquery(self) -> LateralFromClause:
        """Subquery - last message for each chat, lateral to Chat.id"""
        return (
            select(
                Message.id,
                Message.created_at,
                Message.content,
                Message.sender_id,
            )
            .where(Message.chat_id == Chat.id)
            .order_by(Message.id.desc())
            .limit(1)
            .correlate(Chat)
            .lateral("last_messages_subq")
        )

    def _build_first_messages_subquery(self) -> LateralFromClause:
        """Subquery - first message for each chat, lateral to Chat.id"""
        return (
            select(
                Message.id,
                Message.created_at,
                Message.content,
                Message.sender_id,
            )
            .where(Message.chat_id == Chat.id, Message.sender_id.isnot(None))
            .order_by(Message.id.asc())
            .limit(1)
            .correlate(Chat)
            .lateral("first_messages_subq")
        )

    def _build_chat_members_subquery(self) -> LateralFromClause:
        """Subquery - select primary members for chat as JSONB, lateral to Chat.id"""
        return (
            select(
                func.jsonb_agg(
                    func.json_build_object(
                        sqla_text("'user_id'"),
                        ChatMembership.user_id,
                        sqla_text("'user_role'"),
                        ChatMembership.user_role,
                        sqla_text("'is_primary_member'"),
                        ChatMembership.is_primary_member,
                    ),
                ).label("members"),
            )
            .where(ChatMembership.chat_id == Chat.id, ChatMembership.is_archive_member.is_(False))
            .correlate(Chat)
            .lateral("primary_members_subquery")
        )
