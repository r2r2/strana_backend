import contextlib

from google.protobuf.message import Message
from starlette.websockets import WebSocket, WebSocketDisconnect
from websockets.exceptions import ConnectionClosed as WSConnectionClosed

from src.core.logger import LoggerName, get_logger
from src.core.protobuf import pretty_format_pb
from src.exceptions import (
    ConnectionClosedError,
    InvalidMessageTypeError,
    WebsocketError,
)

from .interface import WSConnectionStats, WSTransportProto


class WSTransport(WSTransportProto):
    def __init__(self, raw_connection: WebSocket) -> None:
        self._connection = raw_connection
        self.logger = get_logger(LoggerName.WS)
        self.stats = WSConnectionStats()

    async def close(self, code: int = 1000, reason: str | None = None) -> None:
        with contextlib.suppress(TypeError):  # in case when connection is already closed
            await self._connection.close(code, reason)

    async def send_message(self, message: Message) -> None:
        await self._send_bytes(message.SerializeToString())
        self.logger.debug(f"Sent message {pretty_format_pb(message)}")

    async def receive_message(self) -> bytes:
        return await self._receive_bytes()

    async def _send_bytes(self, data: bytes) -> None:
        try:
            await self._connection.send_bytes(data)
            self.stats.on_message_sent(len(data))

        except (RuntimeError, WebSocketDisconnect, WSConnectionClosed) as exc:
            raise ConnectionClosedError from exc

        except Exception as exc:
            raise WebsocketError(f"Unknown error: {type(exc).__name__} {exc}") from exc

    async def _receive_bytes(self) -> bytes:
        try:
            result = await self._connection.receive_bytes()
            self.stats.on_message_received(len(result))
            return result

        except (RuntimeError, WebSocketDisconnect, AssertionError, TypeError, WSConnectionClosed) as exc:
            raise ConnectionClosedError from exc

        except KeyError as exc:  # Not bytes were sent
            raise InvalidMessageTypeError() from exc

        except Exception as exc:
            raise WebsocketError(f"Unknown error: {type(exc).__name__} {exc}") from exc
