from typing import Protocol

from src.core.common.utility import SupportsHealthCheck
from src.core.types import ConnectionId, UserId
from src.entities.users import Role
from src.modules.chat import ChatMsgTransportProto, LocalConnectionInfo

from .settings import ConnectionsServiceSettings


class ConnectionsServiceProto(SupportsHealthCheck, Protocol):
    settings: ConnectionsServiceSettings

    async def get_all_connections(
        self,
        user_ids: list[int],
        exclude: list[ConnectionId] | None = None,
    ) -> set[tuple[UserId, ConnectionId]]: ...

    async def on_user_connected(
        self,
        user_id: UserId,
        user_role: Role,
        cid: ConnectionId,
        transport: ChatMsgTransportProto,
        ip: str | None,
    ) -> LocalConnectionInfo: ...

    async def connection_closed(self, connection: LocalConnectionInfo) -> None: ...

    async def remove_stale_connection(self, user_id: UserId, cid: ConnectionId) -> None: ...

    def get_connections_count_by_ip(self, ip: str | None) -> int: ...
