from typing import Any

from sl_messenger_protobuf.requests_pb2 import SendActivityCommand

from src.core.common.redis import Throttler
from src.exceptions import NotPermittedError
from src.modules.chat.handlers.base import BaseMessageHandler, handler_for
from src.modules.service_updates.entities import UserIsTypingMessage


@handler_for(SendActivityCommand)
class ActivityHandler(BaseMessageHandler[SendActivityCommand]):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.cached_is_user_in_chat = self._cacher.cached_func(
            self._is_user_in_chat,
            ttl=self.chat_settings.is_user_in_chat_cache_ttl,
            noself=True,
        )
        self._throttler = Throttler(conn=self.redis_conn, namespace="activity_throttle_")
        self.throttled_process_activity = self._throttler.throttled_func(
            self.process_activity,
            throttle_time=self.chat_settings.activity_throttle_time,
        )

    async def __call__(self, message: SendActivityCommand) -> None:
        if message.is_typing:
            await self.process_activity(message)
        else:
            await self.throttled_process_activity(
                f"activity:[{self.connection.user_id}]:[{message.chat_id}]:[{message.is_typing}]",
                message,
            )

    async def _is_user_in_chat(self, chat_id: int, user_id: int) -> bool:
        async with self.storage.connect() as storage_conn:
            return await storage_conn.chats.is_user_in_chat(chat_id=chat_id, user_id=user_id)

    async def process_activity(self, message: SendActivityCommand) -> None:
        await self.presence.set_user_is_active(user_id=self.connection.user_id, role=self.connection.user_role)

        if message.HasField("chat_id"):
            if not await self.cached_is_user_in_chat(chat_id=message.chat_id, user_id=self.connection.user_id):
                raise NotPermittedError(f"User is not a member of the chat {message.chat_id}")

            await self.presence.set_user_using_chat(
                user_id=self.connection.user_id,
                role=self.connection.user_role,
                chat_id=message.chat_id,
            )

            if message.is_typing:
                await self.updates_publisher.publish_update(
                    UserIsTypingMessage(
                        cid=self.connection.cid,
                        chat_id=message.chat_id,
                        user_id=self.connection.user_id,
                        is_typing=message.is_typing,
                    ),
                )
