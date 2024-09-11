from typing import Any

from src.core.common import ProtectedProperty
from src.core.common.rabbitmq import ConnectionHolder, ListenerAMQPArgs, QueueListener, RabbitMQPublisherFactoryProto
from src.core.logger import LoggerName, get_logger
from src.entities.users import Role
from src.jobs.cache import MatchCacheData, MatchScoutCacheData, SLSyncInMemoryCache
from src.jobs.match_scout_changes_listener.entities import SLMatchScoutChangePayload
from src.jobs.match_scout_changes_listener.settings import MatchScoutChangesListenerSettings
from src.jobs.sportlevel_users_sync import SportlevelUsersSyncManagerProto
from src.modules.service_updates import ServiceUpdatesRMQOpts
from src.modules.service_updates.entities import MatchCreated, MatchScoutsChanged
from src.modules.sportlevel.interface import SportlevelServiceProto
from src.modules.storage.interface.storage import StorageServiceProto


class MatchScoutChangesListener:
    amqp_conn = ProtectedProperty[ConnectionHolder]()
    updates_listener = ProtectedProperty[QueueListener[Any]]()

    def __init__(
        self,
        users_sync_manager: SportlevelUsersSyncManagerProto,
        rabbitmq_publisher: RabbitMQPublisherFactoryProto,
        storage: StorageServiceProto,
        settings: MatchScoutChangesListenerSettings,
        sl_client: SportlevelServiceProto,
        matches_cache: SLSyncInMemoryCache[int, MatchCacheData],
    ) -> None:
        self._settings = settings

        self.logger = get_logger(LoggerName.MATCH_SCOUT_CHANGES_LISTENER)
        self.amqp_conn = ConnectionHolder(settings=self._settings.amqp, logger=self.logger.bind(subtype="connection"))
        self._sl_client = sl_client
        self._rabbitmq_publisher = rabbitmq_publisher
        self._storage = storage
        self._matches_cache = matches_cache
        self._users_sync_manager = users_sync_manager

    async def health_check(self) -> bool:
        return all(
            [
                self.updates_listener.is_running,
                await self.amqp_conn.health_check(),
            ],
        )

    async def start(self) -> None:
        if not self._settings.is_enabled:
            return

        await self.amqp_conn.start()
        self.updates_listener = await QueueListener.create(
            logger=self.logger.bind(queue="messages"),
            amqp_args=ListenerAMQPArgs(
                exchange_name=self._settings.updates_exchange_name,
                queue_name=self._settings.queue_name,
                queue_durable=True,
            ),
            channel=await self.amqp_conn.get_channel_from_pool(),
            incoming_message_type=SLMatchScoutChangePayload,
            callback=self._handle_scout_changed_update,
        )
        self.logger.debug("Updates listener started")

    async def stop(self) -> None:
        if not self._settings.is_enabled:
            return

        await self.updates_listener.stop()
        await self.amqp_conn.stop()
        self.logger.debug("Updates listener stopped")

    async def _handle_scout_changed_update(self, update: SLMatchScoutChangePayload) -> None:
        """Handle changed scout update from Sportlevel"""
        self.logger.debug("Handling match scouts update", match_id=update.translation_id)
        db_match = None

        if not (cached_match := self._matches_cache.get(update.translation_id)):
            async with self._storage.connect(autocommit=True) as db_conn:
                if db_match := await db_conn.matches.get_match_by_id(update.translation_id):
                    cached_match = MatchCacheData(
                        fields=db_match.to_basic_fields(),
                        scouts=[
                            MatchScoutCacheData(
                                is_main_scout=scout.is_main_scout,
                                scout_number=scout.scout_number,
                            )
                            for scout in db_match.scouts
                        ],
                        state=db_match.state,
                    )
                    self._matches_cache.update(update.translation_id, cached_match)
                else:
                    self.logger.debug(
                        "Match is not found in messenger db when handling scouts change, will create new match",
                        match_id=update.translation_id,
                    )

        sl_match_info = await self._sl_client.get_match_by_id(update.translation_id)
        if not sl_match_info:
            self.logger.warning(
                "No match info found for match when handling scouts change",
                match_id=update.translation_id,
            )
            return

        for scout in sl_match_info.scouts:
            await self._users_sync_manager.sync_user_from_sl(scout, role=Role.SCOUT)

        if not cached_match and not db_match:
            # Match is not exists in the db, create it
            self._matches_cache.update(
                key=update.translation_id,
                data=MatchCacheData(
                    fields=sl_match_info.to_basic_fields(),
                    scouts=[
                        MatchScoutCacheData(
                            is_main_scout=scout.is_main_scout,
                            scout_number=scout.scout_number,
                        )
                        for scout in sl_match_info.scouts
                    ],
                    state=sl_match_info.state,
                ),
            )
            await self._rabbitmq_publisher[ServiceUpdatesRMQOpts].publish_update(MatchCreated(payload=sl_match_info))

        elif cached_match:
            self._matches_cache.update(
                key=update.translation_id,
                data=MatchCacheData(
                    fields=cached_match.fields,
                    scouts=[
                        MatchScoutCacheData(
                            is_main_scout=scout.is_main_scout,
                            scout_number=scout.scout_number,
                        )
                        for scout in sl_match_info.scouts
                    ],
                    state=cached_match.state,
                ),
            )

            await self._rabbitmq_publisher[ServiceUpdatesRMQOpts].publish_update(
                MatchScoutsChanged(
                    sportlevel_id=update.translation_id,
                    scouts=sl_match_info.scouts,
                )
            )
