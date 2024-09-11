from dataclasses import dataclass
from typing import Protocol

from src.core.types import ProtobufMessage


@dataclass
class WSConnectionStats:
    messages_sent: int = 0
    messages_received: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    client_errors: int = 0
    server_errors: int = 0

    def on_server_error(self) -> None:
        self.server_errors += 1

    def on_client_error(self) -> None:
        self.client_errors += 1

    def on_message_sent(self, byte_size: int) -> None:
        self.messages_sent += 1
        self.bytes_sent += byte_size

    def on_message_received(self, byte_size: int) -> None:
        self.messages_received += 1
        self.bytes_received += byte_size


class WSTransportProto(Protocol):
    stats: WSConnectionStats

    async def close(self, code: int = 1000, reason: str | None = None) -> None: ...

    async def send_message(self, message: ProtobufMessage) -> None: ...

    async def receive_message(self) -> bytes: ...
