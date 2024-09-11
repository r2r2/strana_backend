import asyncio
from typing import Any

from sl_messenger_protobuf.enums_pb2 import MessageSendFailedErrorCode
from sl_messenger_protobuf.requests_pb2 import (
    MessageReadCommand,
    MessageReceivedCommand,
    MessageUnreadCommand,
)
from sl_messenger_protobuf.responses_pb2 import MessageSendFailedUpdate

from src.core.common.redis import Throttler
from src.core.types import ConnectionId, ProtobufMessageT, UserId
from src.entities.messages import DeliveryStatus
from src.modules.chat.handlers.base import BaseMessageHandler, handler_for
from src.modules.service_updates.entities import DeliveryStatusChanged
from src.modules.storage.models.chat import ChatMembership


class MessageStatusUpdateMixin(BaseMessageHandler[ProtobufMessageT]):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.cached_get_chat_membership = self._cacher.cached_func(
            self.get_chat_membership,
            ttl=self.chat_settings.is_user_in_chat_cache_ttl,
            noself=True,
        )
        self.throttler = Throttler(conn=self.redis_conn, namespace="delviery_status_throttle_")
        self.throttled_process_message_status_update = self.throttler.throttled_func(
            self.process_message_status_update,
            throttle_time=self.chat_settings.delivery_status_updated_throttle_time,
        )

    async def process_message_status_update(
        self,
        user_id: UserId,
        message_id: int,
        cid: ConnectionId,
        status: DeliveryStatus,
        mark_as_unread: bool = False,
    ) -> None:
        if not (membership := await self.cached_get_chat_membership(message_id=message_id, user_id=user_id)):
            await self.connection.transport.send_message(
                MessageSendFailedUpdate(
                    error_code=MessageSendFailedErrorCode.MESSAGE_SEND_FAILED_ERROR_CODE_NOT_PERMITTED,
                    error_message=f"The message is unavailable to the user, it cannot be marked as {status.value}",
                ),
            )
            return

        async with self.storage.connect(autocommit=True) as storage_conn:
            if mark_as_unread:
                updated_for_user_count, updated_for_all_count = await storage_conn.messages.update_unread_status(
                    chat_id=membership.chat_id,
                    message_id=message_id,
                    user_id=user_id,
                    new_status=status,
                    update_for_all=membership.has_read_permission,
                )
            else:
                updated_for_user_count, updated_for_all_count = await storage_conn.messages.update_message_status(
                    chat_id=membership.chat_id,
                    message_id=message_id,
                    user_id=user_id,
                    new_status=status,
                    update_for_all=membership.has_read_permission,
                )

        await self.updates_publisher.publish_update(
            DeliveryStatusChanged(
                cid=cid,
                message_id=message_id,
                status=status,
                user_id=user_id,
                chat_id=membership.chat_id,
                updated_for_user=updated_for_user_count,
                updated_for_all=updated_for_all_count,
            ),
        )

    async def get_chat_membership(self, message_id: int, user_id: UserId) -> ChatMembership | None:
        async with self.storage.connect() as storage_conn:
            return await storage_conn.chats.get_chat_membership_by_message_id(message_id=message_id, user_id=user_id)


@handler_for(MessageReadCommand)
class MessageReadCommandHandler(MessageStatusUpdateMixin[MessageReadCommand]):
    async def __call__(self, message: MessageReadCommand) -> None:
        self.logger.debug(f"Message #{message.message_id} read by the user#{self.connection.user_id}")
        await self.throttled_process_message_status_update(
            f"[{self.connection.user_id}]:[{message.message_id}]:[READ]",
            user_id=self.connection.user_id,
            message_id=message.message_id,
            cid=self.connection.cid,
            status=DeliveryStatus.READ,
        )


@handler_for(MessageReceivedCommand)
class MessageReceivedCommandHandler(MessageStatusUpdateMixin[MessageReceivedCommand]):
    async def __call__(self, message: MessageReceivedCommand) -> None:
        self.logger.debug(f"Message #{message.message_id} received by the user#{self.connection.user_id}")
        await self.throttled_process_message_status_update(
            f"[{self.connection.user_id}]:[{message.message_id}]:[DELIVERED]",
            user_id=self.connection.user_id,
            message_id=message.message_id,
            cid=self.connection.cid,
            status=DeliveryStatus.DELIVERED,
        )


@handler_for(MessageUnreadCommand)
class MessageUnreadCommandHandler(MessageStatusUpdateMixin[MessageUnreadCommand]):
    async def __call__(self, message: MessageUnreadCommand) -> None:
        self.logger.debug(f"Message #{message.message_id} marked as unread by the user#{self.connection.user_id}")
        await asyncio.sleep(self.chat_settings.unread_message_delay_sec)
        await self.throttled_process_message_status_update(
            f"[{self.connection.user_id}]:[{message.message_id}]:[DELIVERED]",
            user_id=self.connection.user_id,
            message_id=message.message_id,
            cid=self.connection.cid,
            status=DeliveryStatus.DELIVERED,
            mark_as_unread=True,
        )
