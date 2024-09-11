from datetime import timedelta

from src.core.logger import LoggerName, get_logger
from src.core.types import UserId
from src.entities.users import Role
from src.modules.presence.interface import PackedUserData, PresenceServiceProto
from src.modules.presence.settings import PresenceSettings
from src.modules.presence.storage import PresenceStorage
from src.providers.time import datetime_now, timestamp_now


class PresenceService(PresenceServiceProto):
    """
    Keeps track of online statuses of users.
    """

    def __init__(self, settings: PresenceSettings) -> None:
        self.logger = get_logger(LoggerName.PRESENCE)
        self.settings = settings
        self.storage = PresenceStorage(settings.redis, logger=self.logger.bind(subtype="storage"))

    async def health_check(self) -> bool:
        return await self.storage.health_check()

    async def set_user_is_active(self, user_id: UserId, role: Role) -> None:
        await self.storage.set_last_user_activity(
            user_data=PackedUserData(user_id=user_id, role=role),
            active_at=float(timestamp_now()),
        )

    async def set_user_using_chat(self, user_id: UserId, role: Role, chat_id: int) -> None:
        await self.storage.set_last_chat_activity(
            user_data=PackedUserData(user_id=user_id, role=role),
            chat_id=chat_id,
            active_at=float(timestamp_now()),
        )

    async def get_active_users_in_chats(
        self,
        chat_ids: list[int],
        activity_time: timedelta | None = None,
    ) -> list[PackedUserData]:
        if not activity_time:
            activity_time = self.settings.activity_time_threshold

        threshold = (datetime_now() - activity_time).timestamp()
        return await self.storage.get_active_users_in_chats(chat_ids=chat_ids, active_after=threshold)

    async def get_active_users(
        self,
        filter_by_role: Role | None = None,
        activity_time: timedelta | None = None,
    ) -> list[PackedUserData]:
        if not activity_time:
            activity_time = self.settings.activity_time_threshold

        threshold = (datetime_now() - activity_time).timestamp()
        return await self.storage.get_active_users(threshold, filter_by_role=filter_by_role)
