from typing import Any, Protocol

from sl_messenger_protobuf.messages_pb2 import MessageContent as MessageContentPb

from src.api.http.serializers.messages import UnreadMessage
from src.core.types import UserId
from src.entities.messages import DeliveryStatus, MessageDTO
from src.modules.storage.models.message import Message


class MessageOperationsProtocol(Protocol):
    async def create_message(
        self,
        sender_id: int | None,
        chat_id: int,
        content: MessageContentPb,
        reply_to: int | None = None,
    ) -> Message: ...

    async def update_message(
        self,
        message: Message,
        update_data: dict[str, Any],
    ) -> MessageDTO: ...

    async def update_message_status(
        self,
        chat_id: int,
        message_id: int,
        user_id: UserId,
        new_status: DeliveryStatus,
        update_for_all: bool,
    ) -> tuple[int, int]:
        """
        Update the message delivery status.
        Returns tuple[int, int]:
            0. count of updated statuses for the current user
            1. count of updated statuses for all users
        """
        ...

    async def update_unread_status(
        self,
        chat_id: int,
        message_id: int,
        user_id: UserId,
        new_status: DeliveryStatus,
        update_for_all: bool,
    ) -> tuple[int, int]:
        """
        Update the message delivery status and mark it as unread.
        Returns tuple[int, int]:
            0. count of updated statuses for the current user
            1. count of updated statuses for all users
        """
        ...

    async def get_message_delivery_status(self, user_id: UserId, message_id: int) -> DeliveryStatus: ...

    async def get_chat_id_by_message_id(self, message_id: int) -> int: ...

    async def get_message_by_id(self, message_id: int) -> Message | None: ...

    async def get_messages(
        self,
        chat_id: int,
        user_id: UserId,
        from_message_id: int | None,
        backwards: bool,
        limit: int,
        last_available_message_id: int | None,
    ) -> list[MessageDTO]: ...

    async def add_reaction(
        self,
        message_id: int,
        user_id: UserId,
        emoji: str,
    ) -> int: ...

    async def delete_reaction(
        self,
        message_id: int,
        user_id: UserId,
        emoji: str,
    ) -> int: ...

    async def get_unread_messages(
        self,
        user_id: UserId,
        limit: int,
        offset: int,
    ) -> list[UnreadMessage]: ...
