from typing import Any

from src.core.common import ProtectedProperty
from src.core.common.rabbitmq import ConnectionHolder, ListenerAMQPArgs, QueueListener, RabbitMQPublisherFactoryProto
from src.core.logger import LoggerName, get_logger
from src.entities.matches import MatchState
from src.entities.users import Role
from src.exceptions import InternalError
from src.jobs.cache import MatchCacheData, MatchScoutCacheData, SLSyncInMemoryCache, UserCacheData
from src.jobs.match_state_updates_listener.entities import SLMatchStateUpdatePayload
from src.jobs.match_state_updates_listener.settings import MatchStateUpdatesListenerSettings
from src.jobs.sportlevel_users_sync import SportlevelUsersSyncManagerProto
from src.modules.service_updates import ServiceUpdatesRMQOpts
from src.modules.service_updates.entities import (
    MatchCreated,
    MatchDataChanged,
    MatchScoutsChanged,
    MatchStateChanged,
)
from src.modules.sportlevel.interface import SLMatchState, SportlevelServiceProto
from src.modules.storage.interface.storage import StorageServiceProto


class MatchStateUpdatesListener:
    amqp_conn = ProtectedProperty[ConnectionHolder]()
    updates_listener = ProtectedProperty[QueueListener[Any]]()

    def __init__(
        self,
        users_sync_manager: SportlevelUsersSyncManagerProto,
        rabbitmq_publisher: RabbitMQPublisherFactoryProto,
        storage: StorageServiceProto,
        settings: MatchStateUpdatesListenerSettings,
        sl_client: SportlevelServiceProto,
        matches_cache: SLSyncInMemoryCache[int, MatchCacheData],
        users_cache: SLSyncInMemoryCache[int, UserCacheData],
    ) -> None:
        self._settings = settings

        self.logger = get_logger(LoggerName.MATCH_STATE_UPDATES_LISTENER)
        self.amqp_conn = ConnectionHolder(settings=self._settings.amqp, logger=self.logger.bind(subtype="connection"))
        self._sl_client = sl_client
        self._updates_publisher = rabbitmq_publisher[ServiceUpdatesRMQOpts]
        self._storage = storage
        self._matches_cache = matches_cache
        self._users_cache = users_cache
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
            incoming_message_type=SLMatchStateUpdatePayload,
            callback=self._handle_match_status_update,
        )
        self.logger.debug("Updates listener started")

    async def stop(self) -> None:
        if not self._settings.is_enabled:
            return

        await self.updates_listener.stop()
        await self.amqp_conn.stop()
        self.logger.debug("Updates listener stopped")

    async def _handle_match_status_update(self, update: SLMatchStateUpdatePayload) -> None:
        """Handle match status update from Sportlevel"""
        self.logger.debug(
            "Handling match status update",
            debug_info=update.json(),
        )

        match_state = SLMatchState(update.state_id).to_match_state()

        if not (cached := self._matches_cache.get(update.translation_id)):
            # Match is not cached, try to load state from db
            cached = await self._load_match_to_cache(update.translation_id)
            if not cached:
                # New match, try to load match info from SL
                sl_match_info = await self._sl_client.get_match_by_id(update.translation_id)
                if not sl_match_info:
                    self.logger.info(
                        "Match not found in Sportlevel (or invalid), state update will be skipped",
                        match_id=update.translation_id,
                    )
                    return

                # Ignore new match without scouts
                if not sl_match_info.scouts:
                    self.logger.debug(
                        "Match without scouts, state update will be skipped",
                        match_id=update.translation_id,
                    )
                    return

                self._matches_cache.update(
                    key=sl_match_info.sportlevel_id,
                    data=MatchCacheData(
                        fields=sl_match_info.to_basic_fields(),
                        scouts=[
                            MatchScoutCacheData(
                                scout_number=scout.scout_number,
                                is_main_scout=scout.is_main_scout,
                            )
                            for scout in sl_match_info.scouts
                        ],
                        state=sl_match_info.state,
                    ),
                )
                for scout in sl_match_info.scouts:
                    await self._users_sync_manager.sync_user_from_sl(user=scout, role=Role.SCOUT)

                await self._updates_publisher.publish_update(MatchCreated(payload=sl_match_info))

            else:
                await self._compare_and_update_match_info(
                    match_id=update.translation_id,
                    new_state=match_state,
                    cached=cached,
                )

        else:
            await self._compare_and_update_match_info(
                match_id=update.translation_id,
                new_state=match_state,
                cached=cached,
            )

    async def _load_match_to_cache(self, match_id: int) -> MatchCacheData | None:
        """Load match state from database and update cache"""
        async with self._storage.connect() as db_conn:
            if match_info := await db_conn.matches.get_match_by_id(match_id):
                cacheable_data = MatchCacheData(
                    fields=match_info.to_basic_fields(),
                    scouts=[
                        MatchScoutCacheData(
                            scout_number=scout.scout_number,
                            is_main_scout=scout.is_main_scout,
                        )
                        for scout in match_info.scouts
                    ],
                    state=match_info.state,
                )
                self._matches_cache.update(key=match_id, data=cacheable_data)
                return cacheable_data

            return None

    async def _process_sl_match_info(
        self,
        match_id: int,
        cached: MatchCacheData,
    ) -> None:
        sl_match_info = await self._sl_client.get_match_by_id(match_id)
        if not sl_match_info:
            self.logger.warning(
                "Match not found in Sportlevel, fields update will be skipped",
                match_id=cached,
            )
            return

        self._matches_cache.update(
            key=match_id,
            data=MatchCacheData(
                fields=sl_match_info.to_basic_fields(),
                scouts=[
                    MatchScoutCacheData(scout_number=scout.scout_number, is_main_scout=scout.is_main_scout)
                    for scout in sl_match_info.scouts
                ],
                state=sl_match_info.state,
            ),
        )

        # Compare with old fields
        if cached.is_fields_changed(sl_match_info):
            await self._updates_publisher.publish_update(
                MatchDataChanged(
                    sportlevel_id=sl_match_info.sportlevel_id,
                    fields=sl_match_info.to_basic_fields(),
                ),
            )

        if cached.is_scouts_changed(sl_match_info.scouts):
            await self._updates_publisher.publish_update(
                MatchScoutsChanged(
                    sportlevel_id=sl_match_info.sportlevel_id,
                    scouts=sl_match_info.scouts,
                ),
            )

        for scout in sl_match_info.scouts:
            await self._users_sync_manager.sync_user_from_sl(user=scout, role=Role.SCOUT)

    async def _compare_and_update_match_info(
        self,
        match_id: int,
        new_state: MatchState,
        cached: MatchCacheData,
    ) -> None:
        old_state = cached.state

        self.logger.debug(
            f"Match state {'changed' if old_state != new_state else 'not changed'}:"
            f" {match_id} {old_state.name} -> {new_state.name}"
        )

        match (old_state.is_active, new_state.is_active):
            case _ if old_state == new_state:
                # Re-sync data with sportlevel
                await self._process_sl_match_info(match_id=match_id, cached=cached)

            case (True, False):
                # Update only state and send state change event
                await self._updates_publisher.publish_delayed_update(
                    MatchStateChanged(
                        new_state=new_state,
                        old_state=old_state,
                        sportlevel_id=match_id,
                    ),
                    delay=self._settings.finish_match_update_delay,
                )

            case (False, True):
                await self._process_sl_match_info(match_id=match_id, cached=cached)

                # Additionally update match fields and send state change event
                await self._updates_publisher.publish_update(
                    MatchStateChanged(
                        new_state=new_state,
                        old_state=old_state,
                        sportlevel_id=match_id,
                    ),
                )

            case _:
                raise InternalError(f"Unexpected match state transition: {old_state} -> {new_state}")
