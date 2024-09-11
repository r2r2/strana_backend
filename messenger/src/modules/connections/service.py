from dataclasses import asdict

from src.core.common.redis import is_redis_conn_healthy
from src.core.common.redis.helpers import create_redis_conn_pool
from src.core.logger import LoggerName, get_logger
from src.core.types import ConnectionId, UserId
from src.entities.users import Role
from src.modules.chat import ChatMsgTransportProto, LocalConnectionInfo
from src.modules.connections.interface import ConnectionsServiceProto
from src.modules.connections.local import LocalConnections
from src.modules.connections.settings import ConnectionsServiceSettings


class ConnectionsService(ConnectionsServiceProto):
    """Storage for all active websocket connections to the service"""

    def __init__(self, settings: ConnectionsServiceSettings) -> None:
        self.settings = settings
        self.local_connections = LocalConnections()
        self.logger = get_logger(LoggerName.CONNECTIONS_REGISTRY)
        self._redis_conn = create_redis_conn_pool(settings.redis)

    async def health_check(self) -> bool:
        return await is_redis_conn_healthy(self._redis_conn)

    def get_connections_count_by_ip(self, ip: str | None) -> int:
        return len(
            [conn for conns in self.local_connections.get_connections().values() for conn in conns if conn.ip == ip]
        )

    async def get_all_connections(
        self,
        user_ids: list[int],
        exclude: list[ConnectionId] | None = None,
    ) -> set[tuple[UserId, ConnectionId]]:
        if not user_ids:
            return set()

        result = await self._redis_conn.sunion(keys=[self._key_builder(user_id) for user_id in user_ids])
        connections = {self._unpack_connection_info(conn.decode()) for conn in result}  # type: ignore
        if not exclude:
            return connections

        return {(user_id, cid) for user_id, cid in connections if cid not in exclude}

    async def on_user_connected(
        self,
        user_id: UserId,
        user_role: Role,
        cid: ConnectionId,
        transport: ChatMsgTransportProto,
        ip: str | None,
    ) -> LocalConnectionInfo:
        connection = LocalConnectionInfo(
            cid=cid,
            user_id=user_id,
            user_role=user_role,
            transport=transport,
            ip=ip,
        )
        self.local_connections.add_connection(connection)
        await self._add_redis_connection(user_id, cid)
        self.logger.debug("Connection added", **self._get_server_stats())
        return connection

    async def connection_closed(self, connection: LocalConnectionInfo) -> None:
        self.local_connections.remove_connection(connection)
        await self._remove_redis_connection(connection.user_id, connection.cid)
        self.logger.debug("Connection removed", **asdict(connection.transport.stats), **self._get_server_stats())

    async def remove_stale_connection(self, user_id: UserId, cid: ConnectionId) -> None:
        await self._remove_redis_connection(user_id, cid)

    async def _add_redis_connection(self, user_id: int, cid: ConnectionId) -> None:
        await self._redis_conn.sadd(self._key_builder(user_id), self._pack_connection_info(user_id, cid))

    async def _remove_redis_connection(self, user_id: UserId, cid: ConnectionId) -> None:
        await self._redis_conn.srem(self._key_builder(user_id), self._pack_connection_info(user_id, cid))
        self.logger.debug(
            f"Redis connection removed: {self._key_builder(user_id)} -> {self._pack_connection_info(user_id, cid)}",
        )

    def _key_builder(self, user_id: int) -> str:
        return f"connections:[{user_id}]"

    def _pack_connection_info(self, user_id: UserId, cid: ConnectionId) -> str:
        return f"[{user_id}]:[{cid}]"

    def _unpack_connection_info(self, data: str) -> tuple[UserId, ConnectionId]:
        try:
            parts = [item.strip("[]") for item in data.split(":")]
            return (int(parts[0]), parts[1])

        except Exception as exc:  # pylint: disable=broad-except
            raise ValueError(f"Invalid input for Connection: {data}") from exc

    def _get_server_stats(self) -> dict[str, int]:
        return {
            "active_connections": self.local_connections.active_connections_count,
            "connected_users": self.local_connections.connected_users_count,
        }
