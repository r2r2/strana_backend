from typing import Any, Callable, Generic, Type

from src.core.common.rabbitmq import RabbitMQPublisherFactoryProto
from src.core.common.redis.cacher import RedisCacher
from src.core.logger import LoggerName, get_logger
from src.core.types import ProtobufMessageT, RedisConn
from src.exceptions import ServerError
from src.modules.chat.interface import LocalConnectionInfo
from src.modules.chat.settings import ChatSettings
from src.modules.presence.interface import PresenceServiceProto
from src.modules.service_updates.interface import ServiceUpdatesRMQOpts
from src.modules.storage.interface import StorageServiceProto


class BaseMessageHandler(Generic[ProtobufMessageT]):
    def __init__(
        self,
        connection: LocalConnectionInfo,
        storage: StorageServiceProto,
        presence: PresenceServiceProto,
        rabbitmq_publisher: RabbitMQPublisherFactoryProto,
        redis_conn: RedisConn,
        settings: ChatSettings,
        cacher: RedisCacher,
    ) -> None:
        self.logger = get_logger(LoggerName.MESSAGE_HANDLER)
        self.connection = connection
        self.storage = storage
        self.presence = presence
        self.updates_publisher = rabbitmq_publisher[ServiceUpdatesRMQOpts]
        self.redis_conn = redis_conn
        self._cacher = cacher
        self.chat_settings = settings

    async def __call__(self, message: ProtobufMessageT) -> None: ...


MessageHandler = Type[BaseMessageHandler[ProtobufMessageT]]
_all_handlers: dict[Any, MessageHandler[Any]] = {}


def get_handler_for(message_type: ProtobufMessageT) -> Type[BaseMessageHandler[ProtobufMessageT]]:
    handler = _all_handlers.get(type(message_type).__name__)
    if not handler:
        raise ServerError(f"Handler for the message {type(message_type).__name__} was not found")

    return handler


def handler_for(
    message_type: Type[ProtobufMessageT],
) -> Callable[[MessageHandler[ProtobufMessageT]], MessageHandler[ProtobufMessageT]]:
    def decorator(cls: MessageHandler[ProtobufMessageT]) -> MessageHandler[ProtobufMessageT]:
        if message_type in _all_handlers:
            raise ServerError(f"Duplicate handler for message {message_type.__name__}: {cls.__name__}")

        _all_handlers[message_type.__name__] = cls
        return cls

    return decorator
