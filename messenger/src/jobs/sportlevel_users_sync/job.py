from src.core.common.rabbitmq import RabbitMQPublisherFactoryProto
from src.core.logger import LoggerName, get_logger
from src.entities.matches import MatchScoutData
from src.entities.users import Role
from src.jobs.cache import SLSyncInMemoryCache, UserCacheData
from src.modules.service_updates import ServiceUpdatesRMQOpts
from src.modules.service_updates.entities import UserDataChanged
from src.modules.sportlevel.interface import SportlevelServiceProto
from src.modules.storage.interface import StorageServiceProto
from src.modules.storage.models.user import User

from .interface import SportlevelUsersSyncManagerProto

USERS_PAGE_SIZE = 500


class SportlevelUsersSyncManager(SportlevelUsersSyncManagerProto):
    def __init__(
        self,
        storage: StorageServiceProto,
        sl_client: SportlevelServiceProto,
        rabbitmq_publisher: RabbitMQPublisherFactoryProto,
        users_cache: SLSyncInMemoryCache[int, UserCacheData],
    ) -> None:
        self._logger = get_logger(LoggerName.SL_SYNC)
        self._storage = storage
        self._sl_client = sl_client
        self._updates_publisher = rabbitmq_publisher[ServiceUpdatesRMQOpts]
        self._users_cache = users_cache

    async def run_users_sync(self) -> None:
        offset = 0

        async with self._storage.connect() as db:
            while True:
                chunk, _ = await db.users.search(offset=offset, limit=USERS_PAGE_SIZE)
                for user in chunk:
                    await self.sync_user_from_db(user)

                offset += USERS_PAGE_SIZE
                if len(chunk) < USERS_PAGE_SIZE:
                    break

    async def sync_user_from_sl(self, user: MatchScoutData, role: Role) -> None:
        new_data = UserCacheData(
            id=user.id,
            name=user.name,
            scout_number=user.scout_number,
        )

        cached = self._users_cache.get(user.id)
        if not cached:
            async with self._storage.connect() as db:
                if db_user := await db.users.get_by_id(user_id=user.id):
                    cached = UserCacheData(
                        id=db_user.sportlevel_id,
                        name=db_user.name,
                        scout_number=db_user.scout_number,
                    )

        if not cached or cached != new_data:
            self._logger.info(f"User data changed: {user} ({role})")
            self._users_cache.update(key=user.id, data=new_data)
            await self._updates_publisher.publish_update(
                UserDataChanged(
                    user_id=user.id,
                    scout_number=user.scout_number,
                    name=user.name,
                    role=role,
                )
            )

    async def sync_user_from_db(self, user: User) -> None:
        sl_data = await self._sl_client.get_user_by_id(user_id=user.sportlevel_id)
        if not sl_data:
            self._logger.warning("User not found in Sportlevel", user_id=user.sportlevel_id)
            return

        db_data = UserCacheData(
            id=user.sportlevel_id,
            name=user.name,
            scout_number=user.scout_number,
        )

        if not self._users_cache.get(user.sportlevel_id):
            self._users_cache.update(key=user.sportlevel_id, data=db_data)

        sl_data = UserCacheData(
            id=user.sportlevel_id,
            name=sl_data.name,
            scout_number=sl_data.scout_num,
        )

        if db_data != sl_data:
            self._logger.info(f"User data changed: {sl_data}")
            self._users_cache.update(key=sl_data.id, data=sl_data)
            await self._updates_publisher.publish_update(
                UserDataChanged(
                    user_id=sl_data.id,
                    scout_number=sl_data.scout_number,
                    name=sl_data.name,
                    role=user.role,
                ),
            )
