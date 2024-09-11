from sl_messenger_protobuf.main_pb2 import ServerMessage
from sl_messenger_protobuf.responses_pb2 import UserIsTypingUpdate

from src.core.types import ConnectionId
from src.modules.service_updates.entities import UserIsTypingMessage
from src.modules.service_updates.handlers.base import BaseUpdateHandler


class UserIsTypingUpdateHandler(
    BaseUpdateHandler[UserIsTypingMessage],
    update_type=UserIsTypingMessage,
    check_overtime=True,
):
    async def handle(self, cid: ConnectionId | None, update: UserIsTypingMessage) -> None:
        async with self.storage_srvc.connect() as conn:
            users_in_chat = await conn.chats.get_users_in_chat(update.chat_id)
            user_role = await conn.chats.get_role_in_chat(user_id=update.user_id, chat_id=update.chat_id)

            if not user_role:
                raise RuntimeError(f"User role was not found: {update=}")

        chat_update = ServerMessage(
            user_is_typing_update=UserIsTypingUpdate(
                chat_id=update.chat_id,
                user_id=update.user_id,
                is_typing=update.is_typing,
            ),
        )

        await self._broadcast_updates(
            chat_update,
            user_ids=[user.user_id for user in users_in_chat],
            skip_connection=cid,
        )
