import base64

from fastapi import Depends
from sl_messenger_protobuf.messages_pb2 import MessageContent as MessageContentPb
from sl_messenger_protobuf.messages_pb2 import TextContent

from src.api.http.serializers.messages import UnreadMessagesResponse, UpdateMessageRequest
from src.core.common.rabbitmq import RabbitMQPublisherFactoryProto
from src.core.di import Injected
from src.entities.messages import MessageDTO
from src.entities.users import AuthPayload
from src.modules.service_updates import ServiceUpdatesRMQOpts
from src.modules.service_updates.entities import MessageSentToChat
from src.modules.storage.dependencies import inject_storage
from src.modules.storage.interface import StorageProtocol
from src.modules.storage.models import Message
from src.providers.time import datetime_now


class MessagesController:
    def __init__(
        self,
        storage: StorageProtocol = Depends(inject_storage),
        rabbitmq_publisher: RabbitMQPublisherFactoryProto = Injected[RabbitMQPublisherFactoryProto],
    ) -> None:
        self.storage = storage
        self.updates_publisher = rabbitmq_publisher[ServiceUpdatesRMQOpts]

    async def create_message(
        self,
        *,
        chat_id: int,
        content: MessageContentPb,
        sender_id: int | None = None,
        initiator_id: int | None = None,
        do_not_increment_counter: bool = False,
    ) -> Message:
        message = await self.storage.messages.create_message(
            sender_id=sender_id,
            chat_id=chat_id,
            content=content,
        )
        await self.updates_publisher.publish_update(
            update=MessageSentToChat(
                message_id=message.id,
                chat_id=message.chat_id,
                content_raw=base64.b64encode(content.SerializeToString()).decode(),
                sender_id=sender_id,
                initiator_id=initiator_id,
                msg_created_at=int(message.created_at.timestamp()),
                do_not_increment_counter=do_not_increment_counter,
            ),
        )
        await self.storage.commit_transaction()
        return message

    async def update_message(
        self,
        message: Message,
        payload: UpdateMessageRequest,
    ) -> MessageDTO:
        update_data = payload.model_dump(exclude_unset=True)
        update_data["content"] = MessageContentPb(text=TextContent(text=payload.content)).SerializeToString()

        updated_message = await self.storage.messages.update_message(message=message, update_data=update_data)
        await self.storage.commit_transaction()
        return updated_message

    async def delete_message(self, message: Message) -> None:
        update_data = {"deleted_at": datetime_now()}
        await self.storage.messages.update_message(message=message, update_data=update_data)
        await self.storage.commit_transaction()

    async def get_unread_messages(self, user: AuthPayload, limit: int, offset: int) -> UnreadMessagesResponse:
        tmp_limit = limit + 1
        messages = await self.storage.messages.get_unread_messages(user_id=user.id, limit=tmp_limit, offset=offset)
        return UnreadMessagesResponse(data=messages[:limit], has_next_page=len(messages) == tmp_limit)
