from abc import ABC, abstractmethod
from functools import partial
from typing import Any, Generic, Type, TypeVar
from uuid import uuid4

from src.core.common.caching import CacherProto
from src.core.common.rabbitmq import DropMessageError, RabbitMQPublisherFactoryProto
from src.core.common.redis import RedisPublisher
from src.core.types import ConnectionId, LoggerType, ProtobufMessage, UserId
from src.entities.redis import RedisPubSubChannelName
from src.modules.auth import AuthServiceProto
from src.modules.connections import ConnectionsServiceProto
from src.modules.presence import PresenceServiceProto
from src.modules.service_updates import UpdatesListenerSettings
from src.modules.service_updates.entities import ServiceUpdate
from src.modules.storage import StorageServiceProto
from src.modules.telegram import TelegramServiceProto
from src.providers.time import timestamp_now

UpdateTypeT = TypeVar("UpdateTypeT", bound=ServiceUpdate)


class BaseUpdateHandler(ABC, Generic[UpdateTypeT]):
    _handlers: "dict[Type[ServiceUpdate], Type[BaseUpdateHandler[ServiceUpdate]]]" = {}
    message_type: Type[UpdateTypeT]
    check_overtime: bool

    def __init__(
        self,
        logger: LoggerType,
        settings: UpdatesListenerSettings,
        cacher: CacherProto,
        auth_srvc: AuthServiceProto,
        conn_srvc: ConnectionsServiceProto,
        presence_srvc: PresenceServiceProto,
        storage_srvc: StorageServiceProto,
        telegram_srvc: TelegramServiceProto,
        rabbitmq_publisher: RabbitMQPublisherFactoryProto,
        redis_publisher: RedisPublisher,
    ) -> None:
        self.logger = logger
        self.settings = settings
        self.cacher = cacher
        self.storage_srvc = storage_srvc
        self.conn_srvc = conn_srvc
        self.auth_srvc = auth_srvc
        self.presence_srvc = presence_srvc
        self.telegram_srvc = telegram_srvc
        self.rabbitmq_publisher = rabbitmq_publisher
        self.redis_publisher = redis_publisher
        self._id = str(uuid4())

    def __init_subclass__(
        cls: "Type[BaseUpdateHandler[UpdateTypeT]]",
        update_type: Type[UpdateTypeT],
        check_overtime: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init_subclass__(**kwargs)
        BaseUpdateHandler._handlers[update_type] = cls  # type: ignore
        cls.message_type = update_type
        cls.check_overtime = check_overtime

    @abstractmethod
    async def handle(self, cid: ConnectionId | None, update: UpdateTypeT) -> None: ...

    async def _is_overtime(self, update: ServiceUpdate) -> bool:
        ts_now = timestamp_now()
        time_diff = ts_now - update.created_at
        if time_diff > self.settings.queue_overflow_time_limit:
            self.logger.warning(
                "Too much time has elapsed between the occurrence of an event and the moment it is processed",
                limit=self.settings.queue_overflow_time_limit,
                time_diff=time_diff,
                update_type=update.type.value,
            )
            return True

        return False

    async def _broadcast_updates(
        self,
        update: ProtobufMessage,
        user_ids: list[int],
        skip_user: UserId | None = None,
        skip_connection: ConnectionId | None = None,
    ) -> None:
        if skip_user and skip_user in user_ids:
            user_ids.remove(skip_user)

        connections = await self.conn_srvc.get_all_connections(
            user_ids,
            exclude=[skip_connection] if skip_connection else None,
        )
        if not connections:
            # No connected users found
            return

        for user_id, connection_id in connections:
            self.logger.debug(f"Publishing update {update.WhichOneof('message')} to {user_id=}, {connection_id=}")

            await self.redis_publisher.send_to(
                channel_name=RedisPubSubChannelName.CONNECTION_UPDATES.format(connection_id=connection_id),
                data=update.SerializeToString(),
                on_error=partial(self._on_broadcast_error, cid=connection_id, user_id=user_id),
            )

    async def _on_broadcast_error(self, cid: ConnectionId, user_id: UserId) -> None:
        self.logger.warning("Stale connection found, removing", connection_id=cid, user_id=user_id)
        await self.conn_srvc.remove_stale_connection(cid=cid, user_id=user_id)


async def call_handler(
    *,
    update: ServiceUpdate,
    logger: LoggerType,
    cacher: CacherProto,
    settings: UpdatesListenerSettings,
    auth_srvc: AuthServiceProto,
    conn_srvc: ConnectionsServiceProto,
    presence_srvc: PresenceServiceProto,
    storage_srvc: StorageServiceProto,
    telegram_srvc: TelegramServiceProto,
    rabbitmq_publisher: RabbitMQPublisherFactoryProto,
    redis_publisher: RedisPublisher,
) -> None:
    handler_cls = BaseUpdateHandler._handlers.get(type(update))
    if not handler_cls:
        logger.critical(f"Handler for {update=} was not found")
        return

    handler = handler_cls(
        logger=logger,
        settings=settings,
        cacher=cacher,
        conn_srvc=conn_srvc,
        presence_srvc=presence_srvc,
        storage_srvc=storage_srvc,
        rabbitmq_publisher=rabbitmq_publisher,
        auth_srvc=auth_srvc,
        telegram_srvc=telegram_srvc,
        redis_publisher=redis_publisher,
    )

    if handler_cls.check_overtime and await handler._is_overtime(update):
        raise DropMessageError

    logger.debug(f"Handling {update} ")
    await handler.handle(cid=update.cid, update=update)
