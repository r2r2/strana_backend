import base64
from typing import Any

from sl_messenger_protobuf.enums_pb2 import DeliveryStatus as DeliveryStatusPb
from sl_messenger_protobuf.main_pb2 import ServerMessage
from sl_messenger_protobuf.messages_pb2 import Message
from sl_messenger_protobuf.messages_pb2 import MessageContent as PBMessageContent
from sl_messenger_protobuf.responses_pb2 import MessageReceivedUpdate
from sl_messenger_protobuf.updates_streamer_pb2 import UnreadCountersUpdate

from src.core.common.redis import IncrementManyIfExists
from src.core.types import ConnectionId
from src.entities.redis import RedisPubSubChannelName, UnreadCountCacheKey
from src.entities.users import ChatUserDTO
from src.modules.push_notifications import PushNotificationsRMQOpts, SendPushQueueMessage
from src.modules.service_updates.entities import MessageSentToChat
from src.modules.service_updates.handlers.base import BaseUpdateHandler
from src.modules.storage.models.chat import Chat


class NewMessageUpdateHandler(BaseUpdateHandler[MessageSentToChat], update_type=MessageSentToChat):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._cached_get_chat_info = self.cacher.cached_func(
            self._get_chat_by_id,
            noself=True,
        )
        self.increment_many = IncrementManyIfExists(bind_to=self.redis_publisher.redis_conn)

    @staticmethod
    def is_push_notification_required(content: PBMessageContent) -> bool:
        match content.WhichOneof("content"):
            case "user_joined_chat_notification" | "user_left_chat_notification":  # user joined/left chat
                return False

            case "chat_closed_notification" | "chat_opened_notification":  # chat opened/closed by any reason
                return False

            case "related_ticket_created_notification":  # ticket created
                return False

            case "chat_created_notification":  # chat created
                return False

            case "ticket_closed_notification":  # ticket closed
                return False

            case _:
                return True

    async def _get_chat_by_id(self, chat_id: int) -> Chat | None:
        async with self.storage_srvc.connect() as conn:
            return await conn.chats.get_chat_by_id(chat_id)

    async def handle(self, cid: ConnectionId | None, update: MessageSentToChat) -> None:
        chat_info = await self._cached_get_chat_info(update.chat_id)

        if not chat_info:
            raise RuntimeError(f"Chat was not found: {update=}")

        async with self.storage_srvc.connect() as conn:
            users_in_chat = await conn.chats.get_users_in_chat(update.chat_id)

        await self._update_caches(
            update=update,
            chat_info=chat_info,
            users_in_chat=users_in_chat,
        )

        message_content = PBMessageContent.FromString(base64.b64decode(update.content_raw))

        chat_update = ServerMessage(
            message_received_update=MessageReceivedUpdate(
                message=Message(
                    id=update.message_id,
                    sender_id=update.sender_id,
                    chat_id=update.chat_id,
                    sent_at=update.msg_created_at,
                    content=message_content,
                    state=DeliveryStatusPb.DELIVERY_STATUS_DELIVERED,
                    match_id=chat_info.match_id,
                ),
                chat_type=chat_info.type.to_pb(),
            ),
        )

        await self._broadcast_updates(
            chat_update,
            user_ids=[user.user_id for user in users_in_chat],
            skip_connection=cid,
        )

        if self.is_push_notification_required(message_content):
            await self.rabbitmq_publisher[PushNotificationsRMQOpts].publish_update(
                SendPushQueueMessage(source_event=update),
            )

    async def _update_caches(
        self,
        update: MessageSentToChat,
        chat_info: Chat,
        users_in_chat: list[ChatUserDTO],
    ) -> None:
        users_to_update_cache = [user_info for user_info in users_in_chat if user_info.user_id != update.sender_id]

        incr_keys = [UnreadCountCacheKey.TOTAL.format(user_id=user_info.user_id) for user_info in users_to_update_cache]

        if not update.do_not_increment_counter:
            incr_keys.extend(
                [
                    UnreadCountCacheKey.BY_CHAT.format(user_id=user_info.user_id, chat_id=update.chat_id)
                    for user_info in users_to_update_cache
                ]
            )

            if chat_info.match_id:
                incr_keys.extend(
                    [
                        UnreadCountCacheKey.BY_MATCH.format(user_id=user_info.user_id, match_id=chat_info.match_id)
                        for user_info in users_to_update_cache
                    ]
                )

        incr_result = await self.increment_many(incr_by=1, keys=incr_keys)
        self.logger.info(f"Increment results: {incr_result}")

        if not incr_result:
            return

        pipeline = self.redis_publisher.redis_conn.pipeline()

        for key, value in incr_result.items():
            if "[total]" not in key:
                continue

            user_id = int(UnreadCountCacheKey.TOTAL.parse(key)["user_id"])

            channel_name = RedisPubSubChannelName.UNREAD_COUNTERS_UPDATES.format(user_id=user_id)
            pipeline.publish(
                channel=channel_name,
                message=UnreadCountersUpdate(
                    user_id=user_id,
                    unread_count=value,
                ).SerializeToString(),
            )
            self.logger.debug(f"Publishing unread counters update: {user_id=}, {channel_name=} count={value}")

        await pipeline.execute()
