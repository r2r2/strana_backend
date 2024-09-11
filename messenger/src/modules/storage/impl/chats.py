from datetime import datetime
from itertools import chain

from sqlalchemy import and_, delete, func, select, update
from sqlalchemy import text as sqla_text
from sqlalchemy import true as sqla_true
from sqlalchemy.dialects.postgresql import aggregate_order_by
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.common.utility import exclude_fields
from src.core.types import UserId
from src.entities.chats import (
    ChatBaseInfoDTO,
    ChatInfo,
    ChatMemberDTO,
    ChatMemberInfo,
    ChatMembershipDetailsDTO,
    ChatMeta,
)
from src.entities.matches import ChatType
from src.entities.users import ChatUserDTO, Role
from src.modules.storage.impl.query_builders import ChatsQueryBuilder
from src.modules.storage.interface import ChatOperationsProtocol
from src.modules.storage.models import Chat, ChatMembership, Message
from src.providers.i18n import parse_message_content
from src.providers.time import datetime_now


class ChatOperations(ChatOperationsProtocol):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_chat_version(self, chat_id: int) -> int | None:
        query = select(Chat.version).where(Chat.id == chat_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_chat_by_id(self, chat_id: int) -> Chat | None:
        query = select(Chat).where(Chat.id == chat_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_chat_by_message_id(self, message_id: int) -> Chat | None:
        query = select(Chat).select_from(Message).join(Chat, Message.chat_id == Chat.id).where(Message.id == message_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_chat_membership_details(self, user_id: UserId, chat_id: int) -> ChatMembershipDetailsDTO | None:
        query = (
            select(
                Chat.type.label("chat_type"),
                Chat.is_closed.label("is_chat_closed"),
                (ChatMembership.id.isnot(None)).label("is_member"),
                ChatMembership.user_role,
                ChatMembership.is_primary_member,
                ChatMembership.has_write_permission,
                ChatMembership.is_archive_member,
                ChatMembership.last_available_message_id,
                ChatMembership.first_available_message_id,
            )
            .select_from(Chat)
            .outerjoin(ChatMembership, and_(ChatMembership.chat_id == chat_id, ChatMembership.user_id == user_id))
            .where(Chat.id == chat_id)
        )
        result = await self.session.execute(query)
        row_mapping = result.mappings().fetchone()
        if not row_mapping:
            # Chat not found
            return None

        return ChatMembershipDetailsDTO(**row_mapping)

    async def get_users_in_chat(
        self,
        chat_id: int,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[ChatUserDTO]:
        query = (
            select(ChatMembership.user_id, ChatMembership.user_role, ChatMembership.is_primary_member)
            .select_from(ChatMembership)
            .where(ChatMembership.chat_id == chat_id)
            .order_by(ChatMembership.created_at)
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(query)
        return [ChatUserDTO(**row) for row in result.mappings()]

    async def get_chats_of_user(self, user_id: UserId) -> list[int]:
        query = select(ChatMembership.chat_id).select_from(ChatMembership).where(ChatMembership.user_id == user_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_chat_id_between_users(self, user_1_id: UserId, user_2_id: UserId) -> int | None:
        user_ids = sorted([user_1_id, user_2_id])
        query = (
            select(Chat.id)
            .select_from(Chat)
            .join(ChatMembership, ChatMembership.chat_id == Chat.id)
            .where(
                ChatMembership.user_id.in_(user_ids),
                Chat.type == ChatType.PERSONAL,
                ChatMembership.is_primary_member.is_(True),
            )
            .group_by(Chat.id)
            .having(
                func.array_agg(
                    aggregate_order_by(ChatMembership.user_id, ChatMembership.user_id),
                )
                == user_ids,
            )
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_chat_id_by_message_id(self, message_id: int) -> int:
        query = select(Message.chat_id).select_from(Message).where(Message.id == message_id)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def is_user_in_chat(self, chat_id: int, user_id: UserId) -> bool:
        query = (
            select(ChatMembership.id)
            .select_from(ChatMembership)
            .where(ChatMembership.user_id == user_id, ChatMembership.chat_id == chat_id)
        )
        result = await self.session.execute(query)
        return bool(result.first())

    async def get_chat_membership_by_message_id(self, message_id: int, user_id: int) -> ChatMembership | None:
        query = (
            select(ChatMembership)
            .select_from(Message)
            .join(
                ChatMembership,
                and_(
                    ChatMembership.chat_id == Message.chat_id,
                    ChatMembership.user_id == user_id,
                ),
            )
            .where(Message.id == message_id)
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_chat(
        self,
        match_id: int | None,
        chat_type: ChatType,
        meta: ChatMeta,
    ) -> Chat:
        new_chat = Chat(
            created_at=datetime_now(),
            type=chat_type,
            match_id=match_id,
            is_closed=False,
            version=0,
            updated_at=None,
            meta=meta.model_dump(exclude_defaults=True, exclude_unset=True, exclude_none=True),  # type: ignore
        )
        self.session.add(new_chat)
        await self.session.flush()
        return new_chat

    async def close_chats(self, chat_ids: list[int]) -> None:
        query = (
            update(Chat)
            .values(is_closed=True, updated_at=datetime_now(), version=Chat.version + 1)
            .where(Chat.id.in_(chat_ids))
        )
        await self.session.execute(query)

    async def reopen_chat(self, chat_id: int) -> None:
        query = (
            update(Chat)
            .values(is_closed=False, updated_at=datetime_now(), version=Chat.version + 1)
            .where(Chat.id == chat_id)
        )
        await self.session.execute(query)

    async def update_meta(self, chat_id: int, meta: ChatMeta) -> None:
        updates = chain.from_iterable([key, value] for key, value in meta.dict(exclude_unset=True).items())

        query = (
            update(Chat)
            .values(
                meta=Chat.meta.concat(func.jsonb_build_object(*updates)),
                updated_at=datetime_now(),
                version=Chat.version + 1,
            )
            .where(Chat.id == chat_id)
        )
        await self.session.execute(query)

    async def add_user_to_chat(
        self,
        *,
        user_id: UserId,
        chat_id: int,
        role: Role,
        is_primary_member: bool,
        has_write_permission: bool,
        has_read_permission: bool,
    ) -> bool:
        if await self.is_user_in_chat(chat_id=chat_id, user_id=user_id):
            return False

        membership = ChatMembership(
            user_id=user_id,
            chat_id=chat_id,
            user_role=role,
            last_read_message_id=0,
            last_received_message_id=0,
            has_read_permission=has_read_permission,
            has_write_permission=has_write_permission,
            is_primary_member=is_primary_member,
            created_at=datetime_now(),
            last_available_message_id=None,
            first_available_message_id=None,
            is_archive_member=False,
        )
        self.session.add(membership)
        await self.session.flush()

        await self.update_chat_version(chat_id=chat_id)

        return True

    async def remove_user_from_chat(self, chat_id: int, user_id: UserId) -> bool:
        query = delete(ChatMembership).where(
            ChatMembership.chat_id == chat_id,
            ChatMembership.user_id == user_id,
        )
        result = await self.session.execute(query)

        await self.update_chat_version(chat_id=chat_id)

        return bool(result.rowcount)

    async def get_chats(
        self,
        user_id: UserId,
        user_role: Role,
        chat_type: ChatType | None,
        match_id: int | None,
        limit: int,
        offset: int,
    ) -> list[ChatInfo]:
        builder = ChatsQueryBuilder(user_id=user_id, user_role=user_role)
        query = builder.build_get_chat_list_query(
            match_id=match_id,
            chat_type=chat_type,
            limit=limit,
            offset=offset,
        )
        result = await self.session.execute(query)
        return [
            ChatInfo(
                **exclude_fields(row, exclude={"last_message_content", "first_message_content", "members"}),
                last_message_content=parse_message_content(row.last_message_content),
                first_message_content=parse_message_content(row.first_message_content),
                members=[
                    ChatMemberInfo(
                        user_id=member["user_id"],
                        is_primary_member=member["is_primary_member"],
                    )
                    for member in row.members or []
                ],
            )
            for row in result.mappings().fetchall()
        ]

    async def get_chat(self, user_id: UserId, user_role: Role, chat_id: int) -> ChatInfo | None:
        builder = ChatsQueryBuilder(user_id=user_id, user_role=user_role)
        query = builder.build_get_chat_query(chat_id=chat_id)

        result = (await self.session.execute(query)).first()
        if not result:
            return None

        return ChatInfo(
            **exclude_fields(result._mapping, exclude={"last_message_content", "first_message_content", "members"}),
            last_message_content=parse_message_content(result.last_message_content),
            first_message_content=parse_message_content(result.first_message_content),
            members=[
                ChatMemberInfo(
                    user_id=member["user_id"],
                    is_primary_member=member["is_primary_member"],
                )
                for member in result.members
            ],
        )

    async def get_role_in_chat(self, user_id: UserId, chat_id: int) -> Role | None:
        query = select(ChatMembership.user_role).where(
            ChatMembership.user_id == user_id,
            ChatMembership.chat_id == chat_id,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all_chats_by_match(
        self,
        match_id: int,
        chat_types: list[ChatType] | None = None,
    ) -> list[ChatBaseInfoDTO]:
        query = (
            select(
                Chat.id,
                Chat.type,
                func.jsonb_agg(
                    func.jsonb_build_object(
                        sqla_text("'user_id'"),
                        ChatMembership.user_id,
                        sqla_text("'user_role'"),
                        ChatMembership.user_role,
                    ),
                ).label("primary_members"),
                Chat.is_closed,
                Chat.created_at,
            )
            .select_from(Chat)
            .outerjoin(ChatMembership, ChatMembership.chat_id == Chat.id)
            .where(ChatMembership.is_primary_member.is_(True), Chat.match_id == match_id)
            .group_by(Chat.id, Chat.type)
        )
        if chat_types:
            query = query.where(Chat.type.in_(chat_types))

        result = await self.session.execute(query)
        return [
            ChatBaseInfoDTO(
                id=row["id"],
                chat_type=row["type"],
                created_at=row["created_at"],
                is_closed=row["is_closed"],
                primary_members=[ChatMemberDTO(**member) for member in row["primary_members"]],
            )
            for row in result.mappings().fetchall()
        ]

    async def is_chat_with_scout_exists(self, match_id: int, scout_id: UserId, bookmaker_id: UserId) -> bool:
        chat_ids_subq = (
            select(Chat.id)
            .join(ChatMembership, ChatMembership.chat_id == Chat.id)
            .where(
                Chat.match_id == match_id,
                ChatMembership.user_id == scout_id,
                ChatMembership.user_role == Role.SCOUT,
                ChatMembership.is_primary_member.is_(True),
            )
        )

        find_bookmaker_query = (
            select(ChatMembership.is_primary_member)
            .select_from(ChatMembership)
            .where(
                ChatMembership.chat_id.in_(chat_ids_subq),
                ChatMembership.user_id == bookmaker_id,
                ChatMembership.is_primary_member.is_(True),
            )
        )

        result = await self.session.execute(find_bookmaker_query)
        return result.scalar_one_or_none() or False

    async def update_chat_version(self, chat_id: int) -> None:
        update_chat_q = (
            update(Chat).values(updated_at=datetime_now(), version=Chat.version + 1).where(Chat.id == chat_id)
        )
        await self.session.execute(update_chat_q)

    async def get_inactive_chats_to_close(self, last_message_threshold: datetime) -> list[int]:
        last_message_lateral = (
            select(Message.created_at)
            .where(Message.chat_id == Chat.id)
            .order_by(Message.created_at.desc())
            .correlate(Chat)
            .limit(1)
            .lateral("last_message")
        )
        query = (
            select(Chat.id)
            .join(last_message_lateral, sqla_true())
            .where(
                Chat.type == ChatType.PERSONAL,
                Chat.is_closed.is_(False),
                last_message_lateral.c.created_at <= last_message_threshold,
            )
        )
        result = await self.session.execute(query)
        return list(result.scalars())

    async def update_scout_membership(
        self,
        chat_id: int,
        scout_id: UserId,
        last_available_message_id: int | None = None,
        first_available_message_id: int | None = None,
        is_archive_member: bool = False,
        has_write_permission: bool = True,
    ) -> None:
        update_data = {
            "is_archive_member": is_archive_member,
            "has_write_permission": has_write_permission,
        }
        if last_available_message_id is not None:
            update_data["last_available_message_id"] = last_available_message_id  # type: ignore
        if first_available_message_id is not None:
            update_data["first_available_message_id"] = first_available_message_id  # type: ignore

        query = (
            update(ChatMembership)
            .values(**update_data)
            .where(
                ChatMembership.chat_id == chat_id,
                ChatMembership.user_id == scout_id,
            )
        )
        await self.session.execute(query)
