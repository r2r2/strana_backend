from sl_messenger_protobuf.enums_pb2 import UserStatus
from sl_messenger_protobuf.main_pb2 import ServerMessage
from sl_messenger_protobuf.responses_pb2 import UserStatusChangedUpdate

from src.core.types import ConnectionId
from src.entities.users import PresenceStatus
from src.modules.service_updates.entities import PresenceStatusChanged
from src.modules.service_updates.handlers.base import BaseUpdateHandler


class PresenceStatusChangedUpdateHandler(
    BaseUpdateHandler[PresenceStatusChanged],
    update_type=PresenceStatusChanged,
    check_overtime=True,
):
    async def handle(self, cid: ConnectionId | None, update: PresenceStatusChanged) -> None:
        async with self.storage_srvc.connect() as conn:
            chat_ids = await conn.chats.get_chats_of_user(update.user_id)

        # Get active users who used these chats recently
        active_users = await self.presence_srvc.get_active_users_in_chats(chat_ids=chat_ids)

        pb_status = UserStatus.USER_STATUS_OFFLINE
        if update.status == PresenceStatus.ONLINE:
            pb_status = UserStatus.USER_STATUS_ONLINE

        chat_update = ServerMessage(
            user_status_changed_update=UserStatusChangedUpdate(user_id=update.user_id, status=pb_status),
        )

        await self._broadcast_updates(
            chat_update,
            user_ids=[user.user_id for user in active_users],
            skip_user=update.user_id,
        )
