from dataclasses import dataclass
from typing import Protocol

from starlette.websockets import WebSocket

from src.core.common.websocket_transport import WSTransportProto
from src.core.types import ConnectionId, ProtobufMessage, UserId
from src.entities.users import Role


class ChatMsgTransportProto(WSTransportProto, Protocol):
    async def get_message(self) -> ProtobufMessage: ...


class ChatServiceProto(Protocol):
    async def process_connection(self, web_socket: WebSocket, token: str) -> None: ...


@dataclass(repr=True, kw_only=True, eq=True, slots=True)
class LocalConnectionInfo:
    user_id: UserId
    user_role: Role
    cid: ConnectionId
    transport: ChatMsgTransportProto
    ip: str | None

    def __hash__(self) -> int:
        return hash(self.cid)


ConnectedLocalUsers = dict[UserId, list[LocalConnectionInfo]]
