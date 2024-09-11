from collections import defaultdict
from typing import Any

from sl_messenger_protobuf.messages_pb2 import MessageContent
from sqlalchemy import Row, and_, distinct, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from src.api.http.serializers.messages import UnreadMessage
from src.core.types import UserId
from src.entities.messages import BaseMessageDTO, DeliveryStatus, MessageDTO, Reaction
from src.entities.tickets import TicketStatus
from src.modules.storage.interface import MessageOperationsProtocol
from src.modules.storage.models import Chat, ChatMembership, Message, Ticket, UserReaction
from src.providers.i18n import parse_message_content
from src.providers.time import datetime_now


class MessageOperations(MessageOperationsProtocol):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_message(
        self,
        sender_id: int | None,
        chat_id: int,
        content: MessageContent,
        reply_to: int | None = None,
    ) -> Message:
        msg = Message(
            created_at=datetime_now(),
            sender_id=sender_id,
            chat_id=chat_id,
            content=content.SerializeToString(),
            delivery_status=DeliveryStatus.SENT,
            updated_at=None,
            deleted_at=None,
            reply_to=reply_to,
        )
        self.session.add(msg)
        await self.session.flush()
        return msg

    async def update_message(
        self,
        message: Message,
        update_data: dict[str, Any],
    ) -> MessageDTO:
        for key, value in update_data.items():
            setattr(message, key, value)

        message.updated_at = datetime_now()
        self.session.add(message)
        await self.session.flush()
        return MessageDTO(  # type: ignore
            id=message.id,
            sender_id=message.sender_id,
            chat_id=message.chat_id,
            content=parse_message_content(message.content),
            created_at=message.created_at,
            updated_at=message.updated_at,
            deleted_at=message.deleted_at,
            delivery_status=message.delivery_status,
        )

    async def get_message_by_id(self, message_id: int) -> Message | None:
        query = select(Message).where(Message.id == message_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update_message_status(
        self,
        chat_id: int,
        message_id: int,
        user_id: UserId,
        new_status: DeliveryStatus,
        update_for_all: bool,
    ) -> tuple[int, int]:
        updated_ids_for_user = await self._update_delivery_status_for_self(
            new_status,
            chat_id=chat_id,
            user_id=user_id,
            message_id=message_id,
        )

        updated_for_all_count = 0

        if update_for_all:
            updated_for_all_count = await self._update_msg_delivery_statuses(
                message_ids=updated_ids_for_user,
                status=new_status,
            )

        return len(updated_ids_for_user), updated_for_all_count

    async def update_unread_status(
        self,
        chat_id: int,
        message_id: int,
        user_id: UserId,
        new_status: DeliveryStatus,
        update_for_all: bool,
    ) -> tuple[int, int]:
        updated_ids_for_user = await self._update_delivery_status_as_unread(
            chat_id=chat_id,
            user_id=user_id,
            message_id=message_id,
        )

        updated_for_all_count = 0

        if update_for_all:
            update_statuses_query = (
                update(Message)
                .where(Message.id.in_(updated_ids_for_user), Message.delivery_status == DeliveryStatus.READ)
                .values(delivery_status=new_status)
                .returning(Message.id)
            )
            update_status_result = await self.session.execute(update_statuses_query)
            updated_for_all_count = len(update_status_result.scalars().all())

        return len(updated_ids_for_user), updated_for_all_count

    async def get_chat_id_by_message_id(self, message_id: int) -> int:
        query = select(Message.chat_id).select_from(Message).where(Message.id == message_id)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_message_delivery_status(self, user_id: UserId, message_id: int) -> DeliveryStatus:
        query = select(ChatMembership.last_read_message_id, ChatMembership.last_received_message_id).where(
            ChatMembership.chat_id == (select(Message.chat_id).where(Message.id == message_id).scalar_subquery()),
            ChatMembership.user_id == user_id,
        )
        result = await self.session.execute(query)
        status = result.fetchone()
        if not status:
            return DeliveryStatus.SENT

        last_read_msg_id, last_received_msg_id = status.tuple()
        if last_read_msg_id and message_id <= last_read_msg_id:
            return DeliveryStatus.READ

        if last_received_msg_id and message_id < last_received_msg_id:
            return DeliveryStatus.DELIVERED

        return DeliveryStatus.SENT

    async def _get_reactions_map(self, msg_ids: list[int]) -> dict[int, list[UserReaction]]:
        query = select(UserReaction).where(UserReaction.message_id.in_(msg_ids))
        result = (await self.session.execute(query)).scalars()
        reactions_map = defaultdict(list)
        for reaction in result:
            reactions_map[reaction.message_id].append(reaction)
        return reactions_map

    async def get_messages(
        self,
        chat_id: int,
        user_id: UserId,
        from_message_id: int | None,
        backwards: bool,
        limit: int,
        last_available_message_id: int | None,
    ) -> list[MessageDTO]:
        last_read_msg, last_received_msg = await self._get_delivery_statuses(chat_id, user_id)
        replied_msg = aliased(Message, name="replied_msg")

        query = (
            select(
                Message.id,
                Message.created_at,
                Message.updated_at,
                Message.deleted_at,
                Message.sender_id,
                Message.chat_id,
                Message.delivery_status,
                Message.content,
                replied_msg.id.label("replied_id"),
                replied_msg.created_at.label("replied_created_at"),
                replied_msg.sender_id.label("replied_sender_id"),
                replied_msg.chat_id.label("replied_chat_id"),
                replied_msg.delivery_status.label("replied_delivery_status"),
                replied_msg.content.label("replied_content"),
                replied_msg.updated_at.label("replied_updated_at"),
                replied_msg.deleted_at.label("replied_deleted_at"),
            )
            .select_from(Message)
            .outerjoin(
                ChatMembership,
                and_(
                    ChatMembership.chat_id == chat_id,
                    ChatMembership.user_id == Message.sender_id,
                ),
            )
            .outerjoin(replied_msg, replied_msg.id == Message.reply_to)
            .where(Message.chat_id == chat_id)
            .limit(limit)
        )

        query = query.order_by(Message.id.desc() if backwards else Message.id)

        if from_message_id:
            query = query.where(
                (Message.id < from_message_id) if backwards else (Message.id > from_message_id),
            )

        if last_available_message_id:
            query = query.where(Message.id <= last_available_message_id)

        result = (await self.session.execute(query)).all()

        def _get_status(msg: Row[Any]) -> DeliveryStatus:
            if msg.sender_id == user_id:
                return msg.delivery_status

            if msg.id <= last_read_msg:
                return DeliveryStatus.READ

            if msg.id <= last_received_msg:
                return DeliveryStatus.DELIVERED

            return DeliveryStatus.SENT

        reactions = await self._get_reactions_map(msg_ids=[msg.id for msg in result])

        return [
            MessageDTO(
                id=msg.id,
                sender_id=msg.sender_id,
                chat_id=msg.chat_id,
                content=parse_message_content(msg.content),
                created_at=msg.created_at,
                updated_at=msg.updated_at,
                deleted_at=msg.deleted_at,
                delivery_status=_get_status(msg),
                reactions=self._build_user_reactions(msg=msg, user_id=user_id, reactions=reactions),
                reply_to=BaseMessageDTO(
                    id=msg.replied_id,
                    sender_id=msg.replied_sender_id,
                    chat_id=msg.replied_chat_id,
                    created_at=msg.replied_created_at,
                    delivery_status=msg.replied_delivery_status,
                    content=parse_message_content(msg.replied_content),
                    updated_at=msg.replied_updated_at,
                    deleted_at=msg.replied_deleted_at,
                )
                if msg.replied_id
                else None,
            )
            for msg in result
        ]

    async def get_unread_messages(
        self,
        user_id: UserId,
        limit: int,
        offset: int,
    ) -> list[UnreadMessage]:
        query = (
            select(
                distinct(Message.id).label("message_id"),
                Message.chat_id,
                Ticket.id.label("ticket_id"),
                Ticket.status.label("ticket_status"),
                Chat.type.label("chat_type"),
                Chat.match_id,
            )
            .select_from(Message)
            .join(Chat, Chat.id == Message.chat_id)
            .join(
                ChatMembership,
                and_(
                    ChatMembership.chat_id == Message.chat_id,
                    ChatMembership.user_id == user_id,
                ),
            )
            .outerjoin(
                Ticket,
                and_(
                    Ticket.chat_id == Message.chat_id,
                    Ticket.status.in_((TicketStatus.NEW, TicketStatus.IN_PROGRESS)),
                ),
            )
            .where(
                or_(
                    Message.sender_id != user_id,
                    Message.sender_id.is_(None),
                ),
                Message.delivery_status == DeliveryStatus.DELIVERED,
            )
            .order_by(Message.id.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        return [UnreadMessage(**row) for row in result.mappings().all()]

    def _build_user_reactions(
        self,
        msg: Row[Any],
        user_id: int,
        reactions: dict[int, list[UserReaction]],
    ) -> list[Reaction]:
        msg_reactions = reactions.get(msg.id)
        if not msg_reactions:
            return []
        reactions_map = {}
        for reaction in msg_reactions:
            code = reaction.emoji
            u_id = reaction.user_id
            is_user_reacted = user_id == int(u_id)
            if code not in reactions_map:
                reactions_map[code] = Reaction(
                    code=code, user_ids=[int(u_id)], count=1, is_user_reacted=is_user_reacted
                )
            else:
                reactions_map[code].user_ids.append(int(u_id))
                reactions_map[code].count += 1
                if is_user_reacted:
                    reactions_map[code].is_user_reacted = is_user_reacted

        return list(reactions_map.values())

    async def _get_delivery_statuses(self, chat_id: int, user_id: int) -> tuple[int, int]:
        """Returns a tuple of the ids of the last read and last received chat message by the user"""
        statuses_query = select(
            ChatMembership.last_read_message_id,
            ChatMembership.last_received_message_id,
        ).where(ChatMembership.chat_id == chat_id, ChatMembership.user_id == user_id)
        result = await self.session.execute(statuses_query)
        statuses = result.fetchone()
        if not statuses:
            return 0, 0

        last_read, last_received = statuses.tuple()
        return last_read, last_received

    async def _update_delivery_status_for_self(
        self,
        status: DeliveryStatus,
        /,
        chat_id: int,
        user_id: int,
        message_id: int,
    ) -> list[int]:
        match status:
            case DeliveryStatus.READ:
                prop = ChatMembership.last_read_message_id
                attr_name = "last_read_message_id"
            case DeliveryStatus.DELIVERED:
                prop = ChatMembership.last_received_message_id
                attr_name = "last_received_message_id"
            case _:
                raise ValueError(f"Unexpected delivery status: {status}")

        query = select(Message.id).where(
            Message.chat_id == chat_id,
            Message.id
            > (
                select(func.coalesce(prop, 0))
                .where(ChatMembership.chat_id == chat_id, ChatMembership.user_id == user_id)
                .scalar_subquery()
            ),
            Message.id <= message_id,
            or_(
                Message.sender_id != user_id,
                Message.sender_id.is_(None),
            ),
        )
        result = await self.session.execute(query)
        ids_to_update = result.scalars().all()

        update_q = (
            update(ChatMembership)
            .where(
                ChatMembership.user_id == user_id,
                ChatMembership.chat_id == chat_id,
                prop < message_id,
            )
            .values(**{attr_name: message_id})
            .returning(prop)
        )
        result = await self.session.execute(update_q)
        is_updated = result.scalar_one_or_none()
        if not is_updated:
            return []

        return list(ids_to_update)

    async def _update_delivery_status_as_unread(
        self,
        chat_id: int,
        user_id: int,
        message_id: int,
    ) -> list[int]:
        query = (
            select(Message.id)
            .select_from(Message)
            .where(
                Message.chat_id == chat_id,
                Message.id >= message_id,
                or_(
                    Message.sender_id != user_id,
                    Message.sender_id.is_(None),
                ),
                Message.delivery_status == DeliveryStatus.READ,
            )
        )
        result = await self.session.execute(query)
        ids_to_update = result.scalars().all()

        last_read_message_subquery = (
            select(func.coalesce(func.max(Message.id), 0).label("id"))
            .select_from(Message)
            .where(
                Message.chat_id == chat_id,
                or_(
                    Message.sender_id != user_id,
                    Message.sender_id.is_(None),
                ),
                Message.id < message_id,
                Message.delivery_status == DeliveryStatus.READ,
            )
            .scalar_subquery()
        )

        update_q = (
            update(ChatMembership)
            .where(ChatMembership.user_id == user_id, ChatMembership.chat_id == chat_id)
            .values(last_read_message_id=last_read_message_subquery)
            .returning(ChatMembership.last_read_message_id)
        )
        result = await self.session.execute(update_q)
        is_updated = result.scalar_one_or_none()
        if is_updated is None:
            return []

        return list(ids_to_update)

    async def _update_msg_delivery_statuses(
        self,
        message_ids: list[int],
        status: DeliveryStatus,
    ) -> int:
        match status:
            case DeliveryStatus.READ:
                condition = Message.delivery_status != DeliveryStatus.READ
            case DeliveryStatus.DELIVERED:
                condition = Message.delivery_status.not_in([DeliveryStatus.READ, DeliveryStatus.DELIVERED])
            case _:
                raise ValueError(f"Unexpected delivery status: {status}")

        update_statuses_query = (
            update(Message)
            .where(Message.id.in_(message_ids), condition)
            .values(delivery_status=status)
            .returning(Message.id)
        )
        update_status_result = await self.session.execute(update_statuses_query)
        return len(update_status_result.scalars().all())

    async def add_reaction(self, message_id: int, user_id: int, emoji: str) -> int:
        """
        Add the reaction for the message.
        Returns count of users reacted with this emoji
        """
        reaction = UserReaction(message_id=message_id, user_id=user_id, emoji=emoji, created_at=datetime_now())
        self.session.add(reaction)
        await self.session.flush()
        return await self._reaction_count(message_id, emoji)

    async def delete_reaction(self, message_id: int, user_id: int, emoji: str) -> int:
        """
        Delete the reaction for the message.
        Returns count of users reacted with this emoji
        """
        reaction = await self._get_reaction(message_id, user_id, emoji)
        await self.session.delete(reaction)
        await self.session.flush()
        return await self._reaction_count(message_id, emoji)

    async def _get_reaction(self, message_id: int, user_id: int, emoji: str) -> UserReaction | None:
        query = select(UserReaction).where(
            UserReaction.message_id == message_id,
            UserReaction.user_id == user_id,
            UserReaction.emoji == emoji,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def _reaction_count(self, message_id: int, emoji: str) -> int:
        query = select(func.count(UserReaction.id)).where(
            UserReaction.message_id == message_id,
            UserReaction.emoji == emoji,
        )
        result = await self.session.execute(query)
        return result.scalar_one()
