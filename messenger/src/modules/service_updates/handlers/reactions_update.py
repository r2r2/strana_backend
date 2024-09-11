from sl_messenger_protobuf.main_pb2 import ServerMessage
from sl_messenger_protobuf.responses_pb2 import ReactionUpdate

from src.core.types import ConnectionId
from src.modules.service_updates.entities import ReactionUpdatedMessage
from src.modules.service_updates.handlers.base import BaseUpdateHandler


class ReactionUpdateHandler(BaseUpdateHandler[ReactionUpdatedMessage], update_type=ReactionUpdatedMessage):
    async def handle(self, cid: ConnectionId | None, update: ReactionUpdatedMessage) -> None:
        async with self.storage_srvc.connect() as conn:
            users_in_chat = await conn.chats.get_users_in_chat(update.chat_id)

        chat_update = ServerMessage(
            reaction_update=ReactionUpdate(
                chat_id=update.chat_id,
                user_id=update.user_id,
                emoji=update.emoji,
                emoji_count=update.emoji_count,
                message_id=update.message_id,
                is_deleted=update.is_deleted,
            ),
        )

        await self._broadcast_updates(
            chat_update,
            user_ids=[user.user_id for user in users_in_chat],
        )
