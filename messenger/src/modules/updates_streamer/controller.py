import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import sentry_sdk
from redis.exceptions import ConnectionError as RedisConnectionError
from starlette import status
from starlette.websockets import WebSocket, WebSocketDisconnect

from src.core.common.redis import create_redis_conn_pool
from src.core.common.websocket_transport import WSTransport, WSTransportProto
from src.core.di import Injected
from src.core.logger import LoggerName, get_connection_id, get_logger
from src.exceptions import (
    AuthRequiredError,
    ClientError,
    ConnectionClosedError,
    ServerError,
    ServerShutdownError,
)
from src.modules.auth import AuthServiceProto
from src.modules.storage.interface import StorageServiceProto
from src.modules.updates_streamer.commands_handler import handle_client_command
from src.modules.updates_streamer.entities import ConnectionInfo
from src.modules.updates_streamer.settings import UpdatesStreamerSettings
from src.modules.updates_streamer.subscriptions import StreamerSubscriptionsService

from .interface import StreamerConnServiceProto


class StreamerWebsocketHandler:
    def __init__(
        self,
        settings: UpdatesStreamerSettings = Injected[UpdatesStreamerSettings],
        auth: AuthServiceProto = Injected[AuthServiceProto],
        storage: StorageServiceProto = Injected[StorageServiceProto],
        connections: StreamerConnServiceProto = Injected[StreamerConnServiceProto],
    ) -> None:
        self.logger = get_logger(LoggerName.COUNTERS_STREAMER)

        self._auth = auth
        self._storage = storage
        self._redis_conn = create_redis_conn_pool(settings.redis)
        self.settings = settings
        self.connections = connections
        self.subscriptions = StreamerSubscriptionsService(
            redis_settings=self.settings.redis,
            connections=self.connections,
        )

    @asynccontextmanager
    async def handle_errors(self, transport: WSTransportProto) -> AsyncGenerator[None, None]:
        try:
            yield

        except (ConnectionClosedError, WebSocketDisconnect):
            self.logger.debug("Client disconnected")

        except AuthRequiredError as exc:
            await transport.close(code=status.WS_1002_PROTOCOL_ERROR, reason=exc.message)

        except asyncio.CancelledError as exc:
            await transport.close(code=status.WS_1001_GOING_AWAY, reason=ServerShutdownError.description)
            raise exc

        except RedisConnectionError:
            self.logger.critical("Redis connection lost", exc_info=True)
            await transport.close(code=status.WS_1011_INTERNAL_ERROR, reason="Connection lost")

        except Exception as exc:  # pylint: disable=broad-except
            sentry_sdk.capture_exception(exc)
            self.logger.critical("Unknown exception occured", exc_type=type(exc).__name__, exc_info=True)
            await transport.close(code=status.WS_1011_INTERNAL_ERROR, reason="Unknown error")

    @asynccontextmanager
    async def handle_msg_processing_errors(self, transport: WSTransportProto) -> AsyncGenerator[None, None]:
        try:
            yield

        except ServerError as exc:
            transport.stats.on_server_error()
            await transport.close(code=status.WS_1011_INTERNAL_ERROR, reason=exc.message)

        except ClientError as exc:
            transport.stats.on_client_error()
            await transport.close(code=status.WS_1002_PROTOCOL_ERROR, reason=exc.message)

    async def process_connection(self, web_socket: WebSocket, token: str) -> None:
        connection = None
        transport = WSTransport(web_socket)

        async with self.handle_errors(transport):
            await web_socket.accept()

            token_aud = await self._auth.parse_service_token(token)
            if token_aud is None:
                raise AuthRequiredError("Invalid token")

            if token_aud not in self.settings.aud_whitelist:
                raise AuthRequiredError("Token audience is not allowed")

            connection = ConnectionInfo(cid=get_connection_id(), transport=transport)
            self.connections.add_connection(connection)
            await self.subscriptions.start()
            await self._communicate(connection)

        if connection:
            self.connections.remove_connection(connection.cid)

        if self.subscriptions.is_started:
            await self.subscriptions.stop()

    async def _communicate(
        self,
        connection: ConnectionInfo,
    ) -> None:
        while True:
            async with self.handle_msg_processing_errors(connection.transport):
                message = await connection.transport.receive_message()
                await self._process_message(message=message, connection=connection)

    async def _process_message(
        self,
        message: bytes,
        connection: ConnectionInfo,
    ) -> None:
        self.logger.info(f"Received message: {message}")
        await handle_client_command(self, message, connection)
