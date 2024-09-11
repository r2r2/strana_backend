from src.core.common.rabbitmq import RabbitMQPublisherFactoryProto
from src.core.logger import LoggerName, get_logger
from src.core.types import UserId
from src.entities.users import PresenceStatus
from src.jobs.presence_track.settings import PresenceTrackerSettings
from src.modules.presence.storage import PresenceStorage
from src.modules.service_updates.entities import PresenceStatusChanged
from src.modules.service_updates.interface import ServiceUpdatesRMQOpts
from src.providers.time import datetime_now


class PresenceTrackManager:
    """
    Periodically checks the last action time of connected users
    and sets them offline if they have been inactive for a certain period of time.
    """

    def __init__(
        self,
        rabbitmq_publisher: RabbitMQPublisherFactoryProto,
        settings: PresenceTrackerSettings,
    ) -> None:
        self.logger = get_logger(LoggerName.PRESENCE)
        self.settings = settings
        self.storage = PresenceStorage(settings.redis, logger=self.logger.bind(subtype="storage"))
        self._updates_publisher = rabbitmq_publisher[ServiceUpdatesRMQOpts]
        self._online_users: set[int] = set()

    async def health_check(self) -> bool:
        return await self.storage.health_check()

    async def set_user_offline(self, user_id: UserId) -> None:
        self.logger.debug(f"User {user_id} is offline")
        self._online_users.discard(user_id)
        await self._notify_presence_status_changed(user_id=user_id, new_status=PresenceStatus.OFFLINE)

    async def set_user_online(self, user_id: UserId) -> None:
        self.logger.debug(f"User {user_id} is online")
        self._online_users.add(user_id)
        await self._notify_presence_status_changed(user_id=user_id, new_status=PresenceStatus.ONLINE)

    async def cleanup_presence(self) -> None:
        now = datetime_now()
        threshold = (now - self.settings.cleanup_interval).timestamp()
        await self.storage.cleanup_last_chat_activity(active_before=threshold)

    async def check_presence(self) -> None:
        threshold = (datetime_now() - self.settings.offline_time_threshold).timestamp()
        active_users_ids = {user.user_id for user in await self.storage.get_active_users(active_after=threshold)}

        for user_id in active_users_ids:
            if user_id not in self._online_users:
                await self.set_user_online(user_id)

        disconnected_users = self._online_users.difference(active_users_ids)
        for user_id in disconnected_users:
            await self.set_user_offline(user_id)

    async def _notify_presence_status_changed(self, user_id: UserId, new_status: PresenceStatus) -> None:
        self.logger.debug(f"Notify user#{user_id} is {new_status}")
        await self._updates_publisher.publish_update(
            PresenceStatusChanged(user_id=user_id, status=new_status),
        )
