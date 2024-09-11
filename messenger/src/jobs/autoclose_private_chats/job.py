from sl_messenger_protobuf.enums_pb2 import ChatCloseReason
from sl_messenger_protobuf.messages_pb2 import ChatClosedNotificationContent
from sl_messenger_protobuf.messages_pb2 import MessageContent as MessageContentPb

from src.controllers.messages import MessagesController
from src.core.common.rabbitmq import RabbitMQPublisherFactoryProto
from src.core.logger import LoggerName, get_logger
from src.jobs.autoclose_private_chats.settings import AutoclosePrivateChatsSettings
from src.modules.storage.interface.storage import StorageServiceProto
from src.providers.time import datetime_now


class AutoclosePrivateChatManager:
    def __init__(
        self,
        rabbitmq_publisher: RabbitMQPublisherFactoryProto,
        storage: StorageServiceProto,
        settings: AutoclosePrivateChatsSettings,
    ) -> None:
        self._storage = storage
        self._settings = settings
        self._rabbitmq_publisher = rabbitmq_publisher
        self.logger = get_logger(LoggerName.JOB_AUTOCLOSE_PRIVATE_CHATS)

    async def try_close_chats(self) -> None:
        async with self._storage.connect() as db:
            now = datetime_now()
            threshold = now - self._settings.close_after
            chats_to_close = await db.chats.get_inactive_chats_to_close(last_message_threshold=threshold)
            if not chats_to_close:
                return

            self.logger.debug(f"Found {len(chats_to_close)} chats to close: {chats_to_close}")
            await db.chats.close_chats(chats_to_close)
            await db.commit_transaction()

            messages = MessagesController(storage=db, rabbitmq_publisher=self._rabbitmq_publisher)
            for chat_id in chats_to_close:
                await messages.create_message(
                    chat_id=chat_id,
                    content=MessageContentPb(
                        chat_closed_notification=ChatClosedNotificationContent(
                            reason=ChatCloseReason.CHAT_CLOSE_REASON_MEMBERS_INACTIVITY,
                        ),
                    ),
                    sender_id=None,
                    initiator_id=None,
                )
