import asyncio
from contextlib import asynccontextmanager
from functools import partial
from typing import AsyncGenerator

import sentry_sdk
from redis.exceptions import ConnectionError as RedisConnectionError
from sl_messenger_protobuf.enums_pb2 import ErrorReason
from sl_messenger_protobuf.main_pb2 import ServerMessage
from sl_messenger_protobuf.responses_pb2 import ErrorOccuredUpdate
from starlette import status
from starlette.websockets import WebSocket, WebSocketDisconnect

from src.core.common.rabbitmq import RabbitMQPublisherFactoryProto
from src.core.common.redis import RedisListener, create_redis_conn_pool
from src.core.common.redis.cacher import RedisCacher
from src.core.di import Injected
from src.core.logger import LoggerName, get_connection_id, get_logger
from src.core.protobuf import pretty_format_pb
from src.core.types import ProtobufMessage
from src.entities.redis import RedisPubSubChannelName
from src.exceptions import (
    AuthRequiredError,
    ClientError,
    ConnectionClosedError,
    InsufficientPrivilegesError,
    InvalidAuthCredentialsError,
    ServerError,
    ServerShutdownError,
)
from src.modules.auth import AuthServiceProto
from src.modules.chat import ChatMsgTransportProto, LocalConnectionInfo
from src.modules.chat.handlers.base import get_handler_for
from src.modules.chat.interface import ChatServiceProto
from src.modules.chat.settings import ChatSettings
from src.modules.chat.transport import ChatWebsocketTransport
from src.modules.connections.interface import ConnectionsServiceProto
from src.modules.presence.interface import PresenceServiceProto
from src.modules.storage.interface import StorageServiceProto


class ChatService(ChatServiceProto):
    def __init__(
        self,
        settings: ChatSettings = Injected[ChatSettings],
        auth: AuthServiceProto = Injected[AuthServiceProto],
        storage: StorageServiceProto = Injected[StorageServiceProto],
        connections: ConnectionsServiceProto = Injected[ConnectionsServiceProto],
        presence: PresenceServiceProto = Injected[PresenceServiceProto],
        rabbitmq_publisher: RabbitMQPublisherFactoryProto = Injected[RabbitMQPublisherFactoryProto],
    ) -> None:
        self.logger = get_logger(LoggerName.WS)

        self._auth = auth
        self._connections = connections
        self._presence = presence
        self._storage = storage
        self._rabbitmq_publisher = rabbitmq_publisher
        self._redis_conn = create_redis_conn_pool(settings.redis)
        self._settings = settings
        self._cacher = RedisCacher(settings=settings.redis, alias="chat")

    @asynccontextmanager
    async def handle_errors(self, transport: ChatMsgTransportProto) -> AsyncGenerator[None, None]:
        try:
            yield

        except (ConnectionClosedError, WebSocketDisconnect):
            self.logger.debug("Client disconnected")

        except AuthRequiredError as exc:
            await transport.close(code=status.WS_1002_PROTOCOL_ERROR, reason=exc.message)

        except InvalidAuthCredentialsError as exc:
            await transport.close(code=status.WS_1003_UNSUPPORTED_DATA, reason=exc.message)

        except InsufficientPrivilegesError as exc:
            await transport.close(code=status.WS_1008_POLICY_VIOLATION, reason=exc.message)

        except asyncio.CancelledError as exc:
            await transport.close(code=status.WS_1001_GOING_AWAY, reason=ServerShutdownError.description)
            raise exc

        except RedisConnectionError:
            self.logger.critical("Redis connection lost", exc_info=True)
            await transport.send_message(
                ErrorOccuredUpdate(
                    reason=ErrorReason.ERROR_REASON_SERVER,
                    description="Database connection lost, please reconnect",
                ),
            )

        except Exception as exc:  # pylint: disable=broad-except
            sentry_sdk.capture_exception(exc)
            self.logger.critical("Unknown exception occured", exc_info=True)
            await transport.send_message(
                ErrorOccuredUpdate(
                    reason=ErrorReason.ERROR_REASON_SERVER,
                    description=f"{type(exc).__name__}: {str(exc.args)}",
                ),
            )

    @asynccontextmanager
    async def handle_msg_processing_errors(self, transport: ChatMsgTransportProto) -> AsyncGenerator[None, None]:
        try:
            yield

        except ServerError as exc:
            transport.stats.on_server_error()
            await transport.send_message(
                ErrorOccuredUpdate(
                    reason=ErrorReason.ERROR_REASON_SERVER,
                    description=exc.message,
                ),
            )

        except ClientError as exc:
            transport.stats.on_client_error()
            await transport.send_message(
                ErrorOccuredUpdate(
                    reason=ErrorReason.ERROR_REASON_CLIENT,
                    description=exc.message,
                ),
            )

    async def process_connection(self, web_socket: WebSocket, token: str) -> None:
        connection = None
        user = None
        transport = ChatWebsocketTransport(web_socket)

        async with self.handle_errors(transport):
            await web_socket.accept()

            user = await self._auth.process_credentials(token)

            connection = await self._connections.on_user_connected(
                user_id=user.id,
                user_role=user.role,
                cid=get_connection_id(),
                transport=transport,
                ip=web_socket.client.host if web_socket.client else None,
            )

            updates_listener = RedisListener(
                conn=self._redis_conn,
                callback=partial(self._handle_update, transport=transport),
            )
            async with updates_listener:
                await updates_listener.subscribe(
                    RedisPubSubChannelName.CONNECTION_UPDATES.format(connection_id=connection.cid)
                )
                await self._communicate(connection)

        if connection:
            await self._connections.connection_closed(connection=connection)

    async def _handle_update(self, update: bytes, *, transport: ChatMsgTransportProto) -> None:
        command_wrapper = ServerMessage.FromString(update)
        message_type = command_wrapper.WhichOneof("message")
        message = getattr(command_wrapper, message_type)  # type: ignore

        self.logger.debug(f"Received command to send: {pretty_format_pb(message)}")

        try:
            await transport.send_message(message)
        except (ConnectionClosedError, asyncio.CancelledError):
            return

    async def _communicate(
        self,
        connection: LocalConnectionInfo,
    ) -> None:
        while True:
            async with self.handle_msg_processing_errors(connection.transport):
                message = await connection.transport.get_message()
                await self._process_message(message=message, connection=connection)

    async def _process_message(
        self,
        message: ProtobufMessage,
        connection: LocalConnectionInfo,
    ) -> None:
        handler = get_handler_for(message)(
            connection=connection,
            storage=self._storage,
            presence=self._presence,
            rabbitmq_publisher=self._rabbitmq_publisher,
            redis_conn=self._redis_conn,
            settings=self._settings,
            cacher=self._cacher,
        )
        await handler(message)
