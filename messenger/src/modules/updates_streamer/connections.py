from src.core.types import ConnectionId, UserId
from src.modules.updates_streamer.entities import ConnectionInfo

from .interface import StreamerConnServiceProto


class StreamerConnManager(StreamerConnServiceProto):
    def __init__(self) -> None:
        self._connections: dict[ConnectionId, ConnectionInfo] = {}

    @property
    def connections(self) -> dict[ConnectionId, ConnectionInfo]:
        return self._connections

    def get_connections_with_online_users(self, user_ids: list[UserId]) -> list[ConnectionInfo]:
        return [
            connection for connection in self._connections.values() if connection.online_user_ids.intersection(user_ids)
        ]

    def add_connection(self, connection: ConnectionInfo) -> None:
        self._connections[connection.cid] = connection

    def remove_connection(self, cid: ConnectionId) -> None:
        self._connections.pop(cid, None)
