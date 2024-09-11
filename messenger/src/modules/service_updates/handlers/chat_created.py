from sl_messenger_protobuf.main_pb2 import ServerMessage
from sl_messenger_protobuf.responses_pb2 import ChatCreatedUpdate

from src.core.types import ConnectionId
from src.modules.service_updates.entities import ChatCreated
from src.modules.service_updates.handlers.base import BaseUpdateHandler


class ChatCreatedUpdateHandler(BaseUpdateHandler[ChatCreated], update_type=ChatCreated):
    async def handle(self, cid: ConnectionId | None, update: ChatCreated) -> None:
        async with self.storage_srvc.connect() as db_conn:
            chat_members = await db_conn.chats.get_users_in_chat(chat_id=update.chat_id)
            target_user_ids = [member.user_id for member in chat_members if member.is_primary_member]

        await self._broadcast_updates(
            ServerMessage(
                chat_created_update=ChatCreatedUpdate(
                    chat_id=update.chat_id,
                    created_by_user_id=update.created_by_user_id,
                    match_id=update.match_id,
                    chat_type=update.chat_type.to_pb(),
                ),
            ),
            user_ids=target_user_ids,
        )
