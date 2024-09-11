from typing import Protocol

from src.core.common.utility import SupportsHealthCheck, SupportsLifespan
from src.core.types import ConnectionId, UserId
from src.modules.updates_streamer.entities import ConnectionInfo


class StreamerConnServiceProto(Protocol):
    @property
    def connections(self) -> dict[ConnectionId, ConnectionInfo]: ...

    def get_connections_with_online_users(self, user_ids: list[UserId]) -> list[ConnectionInfo]: ...

    def add_connection(self, connection: ConnectionInfo) -> None: ...

    def remove_connection(self, cid: ConnectionId) -> None: ...


class StreamerSubsServiceProto(SupportsHealthCheck, SupportsLifespan, Protocol):
    async def add_sub(self, user_id: UserId) -> None: ...

    async def remove_sub(self, user_id: UserId) -> None: ...
