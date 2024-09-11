from typing import Any

from sl_messenger_protobuf.main_pb2 import ServerMessage
from sl_messenger_protobuf.responses_pb2 import DeliveryStatusChangedUpdate
from sl_messenger_protobuf.updates_streamer_pb2 import UnreadCountersUpdate

from src.core.common.redis import DecrementManyIfExists
from src.core.types import ConnectionId
from src.entities.messages import DeliveryStatus
from src.entities.redis import RedisPubSubChannelName, UnreadCountCacheKey
from src.modules.service_updates.entities import DeliveryStatusChanged
from src.modules.service_updates.handlers.base import BaseUpdateHandler
from src.modules.storage.models.chat import Chat


class DeliveryStatusChangedUpdateHandler(BaseUpdateHandler[DeliveryStatusChanged], update_type=DeliveryStatusChanged):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._cached_get_chat_info = self.cacher.cached_func(
            self._get_chat_by_message_id,
            noself=True,
        )
        self.decrement_many = DecrementManyIfExists(bind_to=self.redis_publisher.redis_conn)

    async def _get_chat_by_message_id(self, message_id: int) -> Chat | None:
        async with self.storage_srvc.connect() as conn:
            return await conn.chats.get_chat_by_message_id(message_id)

    async def handle(self, cid: ConnectionId | None, update: DeliveryStatusChanged) -> None:
        chat_info = await self._cached_get_chat_info(update.message_id)

        if not chat_info:
            raise RuntimeError(f"Chat was not found: {update=}")

        async with self.storage_srvc.connect() as conn:
            users_in_chat = await conn.chats.get_users_in_chat(chat_info.id)

        await self._update_caches(update, chat_info)

        if update.updated_for_user > 0:
            # Send the update only to the user who initiated the action
            await self._broadcast_updates(
                ServerMessage(
                    delivery_status_changed_update=DeliveryStatusChangedUpdate(
                        message_id=update.message_id,
                        state=update.status.to_pb(),
                        read_by=update.user_id,
                        chat_id=update.chat_id,
                        match_id=chat_info.match_id,
                        updated_count=update.updated_for_user,
                        chat_type=chat_info.type.to_pb(),
                    ),
                ),
                user_ids=[update.user_id],
                skip_connection=cid,
            )

        if update.updated_for_all > 0:
            # Send the update to all chat users except the one who initiated the action
            await self._broadcast_updates(
                ServerMessage(
                    delivery_status_changed_update=DeliveryStatusChangedUpdate(
                        message_id=update.message_id,
                        state=update.status.to_pb(),
                        read_by=update.user_id,
                        chat_id=update.chat_id,
                        updated_count=update.updated_for_all,
                        chat_type=chat_info.type.to_pb(),
                        match_id=chat_info.match_id,
                    ),
                ),
                user_ids=[user.user_id for user in users_in_chat],
                skip_connection=cid,
                skip_user=update.user_id,
            )

    async def _update_caches(
        self,
        update: DeliveryStatusChanged,
        chat_info: Chat,
    ) -> None:
        if update.status == DeliveryStatus.READ and update.updated_for_user > 0:
            decr_keys = [
                UnreadCountCacheKey.BY_CHAT.format(user_id=update.user_id, chat_id=update.chat_id),
                UnreadCountCacheKey.TOTAL.format(user_id=update.user_id),
            ]

            if chat_info.match_id:
                decr_keys.append(
                    UnreadCountCacheKey.BY_MATCH.format(user_id=update.user_id, match_id=chat_info.match_id),
                )

            decrement_result = await self.decrement_many(
                decr_by=update.updated_for_user,
                keys=decr_keys,
            )

            self.logger.debug(f"Unread count after decrement: {decrement_result}")

            if (
                decremented_to := decrement_result.get(UnreadCountCacheKey.TOTAL.format(user_id=update.user_id))
            ) is not None:
                await self.redis_publisher.publish(
                    channel_name=RedisPubSubChannelName.UNREAD_COUNTERS_UPDATES.format(user_id=update.user_id),
                    data=UnreadCountersUpdate(user_id=update.user_id, unread_count=decremented_to).SerializeToString(),
                    warn_no_consumers_found=False,
                )
