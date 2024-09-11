from sl_messenger_protobuf.updates_streamer_pb2 import StreamerUpdate, UnreadCountersUpdate

from src.core.common.redis import RedisListener, RedisSettings, create_redis_conn_pool
from src.core.logger import get_logger
from src.core.protobuf import pretty_format_pb
from src.core.types import UserId
from src.entities.redis import RedisPubSubChannelName

from .interface import StreamerConnServiceProto, StreamerSubsServiceProto


class StreamerSubscriptionsService(StreamerSubsServiceProto):
    def __init__(
        self,
        redis_settings: RedisSettings,
        connections: StreamerConnServiceProto,
    ) -> None:
        self.logger = get_logger("streamer_subs")
        self._connections = connections
        self._listener = RedisListener(
            conn=create_redis_conn_pool(redis_settings),
            callback=self._handle_update,
        )
        self._is_started = False
        self._active_subs = set[UserId]()

    @property
    def is_started(self) -> bool:
        return self._is_started

    async def health_check(self) -> bool:
        return await self._listener.health_check()

    async def add_sub(self, user_id: UserId) -> None:
        if user_id in self._active_subs:
            return

        tpl = RedisPubSubChannelName.UNREAD_COUNTERS_UPDATES.format(user_id=user_id)
        await self._listener.subscribe(tpl)
        self._active_subs.add(user_id)
        self.logger.debug(f"Subscribed to {tpl}")

    async def remove_sub(self, user_id: UserId) -> None:
        if user_id not in self._active_subs:
            return

        tpl = RedisPubSubChannelName.UNREAD_COUNTERS_UPDATES.format(user_id=user_id)
        await self._listener.unsubscribe(tpl)
        self._active_subs.remove(user_id)
        self.logger.debug(f"Unsubscribed from {tpl}")

    async def start(self) -> None:
        await self._listener.start()
        self._is_started = True
        self.logger.debug("Started")

    async def stop(self) -> None:
        await self._listener.stop()
        self._is_started = False
        self._active_subs.clear()
        self.logger.debug("Stopped")

    async def _handle_update(self, update: bytes) -> None:
        try:
            msg = UnreadCountersUpdate.FromString(update)
        except Exception as exc:
            self.logger.error("Failed to parse update: %s", exc)
            return

        self.logger.debug(f"Received update: {pretty_format_pb(msg)}")
        user_id = msg.user_id
        if not user_id:
            self.logger.warning(f"Received update without user_id: {pretty_format_pb(update)}")
            return

        for connection in self._connections.get_connections_with_online_users(user_ids=[user_id]):
            self.logger.debug(f"Sending update to connection {connection}")
            await connection.transport.send_message(StreamerUpdate(unread_counters_update=msg))
