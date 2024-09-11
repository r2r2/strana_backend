import base64

from sl_messenger_protobuf.main_pb2 import ServerMessage
from sl_messenger_protobuf.messages_pb2 import MessageContent as PBMessageContent
from sl_messenger_protobuf.responses_pb2 import MessageDeletedUpdate, MessageEditedUpdate

from src.core.types import ConnectionId
from src.modules.service_updates.entities import MessageDeleted, MessageEdited
from src.modules.service_updates.handlers.base import BaseUpdateHandler


class EditMessageHandler(BaseUpdateHandler[MessageEdited], update_type=MessageEdited):
    async def handle(self, cid: ConnectionId | None, update: MessageEdited) -> None:
        async with self.storage_srvc.connect() as conn:
            users_in_chat = await conn.chats.get_users_in_chat(update.chat_id)

        chat_update = ServerMessage(
            message_edited_update=MessageEditedUpdate(
                chat_id=update.chat_id,
                message_id=update.message_id,
                content=PBMessageContent.FromString(base64.b64decode(update.content_raw)),
            ),
        )

        await self._broadcast_updates(
            chat_update,
            user_ids=[user.user_id for user in users_in_chat],
        )


class DeleteMessageHandler(BaseUpdateHandler[MessageDeleted], update_type=MessageDeleted):
    async def handle(self, cid: ConnectionId | None, update: MessageDeleted) -> None:
        async with self.storage_srvc.connect() as conn:
            users_in_chat = await conn.chats.get_users_in_chat(update.chat_id)

        chat_update = ServerMessage(
            message_deleted_update=MessageDeletedUpdate(
                chat_id=update.chat_id,
                message_id=update.message_id,
            ),
        )

        await self._broadcast_updates(
            chat_update,
            user_ids=[user.user_id for user in users_in_chat],
        )
