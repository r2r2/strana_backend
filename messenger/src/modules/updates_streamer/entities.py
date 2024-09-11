from dataclasses import dataclass, field

from src.core.common.websocket_transport import WSTransportProto
from src.core.types import ConnectionId, UserId


@dataclass(repr=True, kw_only=True)
class ConnectionInfo:
    cid: ConnectionId
    online_user_ids: set[UserId] = field(default_factory=set)
    transport: WSTransportProto
