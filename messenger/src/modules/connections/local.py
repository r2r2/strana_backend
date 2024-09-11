from dataclasses import dataclass, field

from src.modules.chat.interface import ConnectedLocalUsers, LocalConnectionInfo


@dataclass(repr=True)
class LocalConnections:
    _connections: ConnectedLocalUsers = field(default_factory=dict)

    @property
    def connected_users_count(self) -> int:
        return len(self._connections)

    @property
    def active_connections_count(self) -> int:
        return sum(len(conn) for conn in self._connections.values())

    def get_connections(self, include_user_ids: list[int] | None = None) -> ConnectedLocalUsers:
        if not include_user_ids:
            return self._connections

        return {
            user_id: connections for user_id, connections in self._connections.items() if user_id in include_user_ids
        }

    def add_connection(self, connection: LocalConnectionInfo) -> None:
        self._connections.setdefault(connection.user_id, []).append(connection)

    def remove_connection(self, connection: LocalConnectionInfo) -> None:
        self._connections[connection.user_id].remove(connection)

        if not self._connections[connection.user_id]:
            del self._connections[connection.user_id]
