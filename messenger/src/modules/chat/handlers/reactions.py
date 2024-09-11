from typing import Any

from sl_messenger_protobuf.enums_pb2 import MessageSendFailedErrorCode
from sl_messenger_protobuf.requests_pb2 import SendReactionCommand
from sl_messenger_protobuf.responses_pb2 import MessageSendFailedUpdate

from src.core.types import UserId
from src.modules.chat.handlers import BaseMessageHandler, handler_for
from src.modules.service_updates.entities import ReactionUpdatedMessage
from src.modules.storage.models import ChatMembership


@handler_for(SendReactionCommand)
class ReactionsHandler(BaseMessageHandler[SendReactionCommand]):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.cached_get_chat_membership = self._cacher.cached_func(
            self.get_chat_membership,
            ttl=self.chat_settings.is_user_in_chat_cache_ttl,
            noself=True,
        )

    async def __call__(self, message: SendReactionCommand) -> None:
        if not (
            membership := await self.cached_get_chat_membership(
                message_id=message.message_id, user_id=self.connection.user_id
            ),
        ):
            await self.connection.transport.send_message(
                MessageSendFailedUpdate(
                    error_code=MessageSendFailedErrorCode.MESSAGE_SEND_FAILED_ERROR_CODE_NOT_PERMITTED,
                    error_message="The message is unavailable to the user, he can not react to it",
                ),
            )
            return

        self.logger.debug(f"Reaction '{message.emoji}' received from the user#{self.connection.user_id}")
        async with self.storage.connect(autocommit=True) as storage_conn:
            if message.is_deleted:
                emoji_count = await storage_conn.messages.delete_reaction(
                    message_id=message.message_id,
                    user_id=self.connection.user_id,
                    emoji=message.emoji,
                )
            else:
                emoji_count = await storage_conn.messages.add_reaction(
                    message_id=message.message_id,
                    user_id=self.connection.user_id,
                    emoji=message.emoji,
                )

        await self.updates_publisher.publish_update(
            ReactionUpdatedMessage(
                cid=self.connection.cid,
                user_id=self.connection.user_id,
                chat_id=membership.chat_id,  # type: ignore
                emoji=message.emoji,
                message_id=message.message_id,
                emoji_count=emoji_count,
                is_deleted=message.is_deleted,
            ),
        )

    async def get_chat_membership(self, message_id: int, user_id: UserId) -> ChatMembership | None:
        async with self.storage.connect() as storage_conn:
            return await storage_conn.chats.get_chat_membership_by_message_id(message_id=message_id, user_id=user_id)
