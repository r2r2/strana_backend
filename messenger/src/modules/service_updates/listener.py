from aio_pika.exchange import ExchangeType

from src.core.common import ProtectedProperty
from src.core.common.caching import CacherProto
from src.core.common.rabbitmq import (
    ConnectionHolder,
    DropMessageError,
    ListenerAMQPArgs,
    QueueListener,
    RabbitMQPublisherFactoryProto,
)
from src.core.common.redis import RedisPublisher, create_redis_conn_pool
from src.core.logger import LoggerName, get_logger
from src.modules.auth.interface import AuthServiceProto
from src.modules.connections import ConnectionsServiceProto
from src.modules.presence import PresenceServiceProto
from src.modules.service_updates.entities import IncomingServiceUpdateModel, ServiceUpdate
from src.modules.service_updates.handlers.base import call_handler
from src.modules.service_updates.interface import ServiceUpdatesRMQOpts, UpdatesListenerProto
from src.modules.service_updates.settings import UpdatesListenerSettings
from src.modules.storage import StorageServiceProto
from src.modules.telegram import TelegramServiceProto


class UpdatesListenerService(UpdatesListenerProto):
    amqp_conn = ProtectedProperty[ConnectionHolder]()
    updates_listener = ProtectedProperty[QueueListener[ServiceUpdate]]()

    def __init__(
        self,
        cacher: CacherProto,
        settings: UpdatesListenerSettings,
        auth_service: AuthServiceProto,
        conn_service: ConnectionsServiceProto,
        presence_service: PresenceServiceProto,
        storage_service: StorageServiceProto,
        telegram_service: TelegramServiceProto,
        rabbitmq_publisher: RabbitMQPublisherFactoryProto,
    ) -> None:
        self.logger = get_logger(LoggerName.UPDATES_LISTENER)
        self.settings = settings

        self.cacher = cacher
        self.auth_srvc = auth_service
        self.storage_srvc = storage_service
        self.conn_srvc = conn_service
        self.presence_srvc = presence_service
        self.telegram_srvc = telegram_service
        self.rabbitmq_publisher = rabbitmq_publisher

        self.amqp_conn = ConnectionHolder(settings=self.settings.amqp, logger=self.logger.bind(subtype="connection"))
        self.redis_publisher = RedisPublisher(
            conn=create_redis_conn_pool(settings.publisher_redis),
            jobs_warning_threshold=settings.publisher_jobs_warning_threshold,
            max_concurrent_jobs=settings.publisher_max_concurrent_jobs,
            max_pending_jobs=settings.publisher_max_pending_jobs,
        )

    async def health_check(self) -> bool:
        return all(
            [
                self.updates_listener.is_running,
                await self.redis_publisher.health_check(),
                await self.amqp_conn.health_check(),
            ],
        )

    async def start(self) -> None:
        await self.amqp_conn.start()
        self.updates_listener = await QueueListener.create(
            logger=self.logger.bind(queue="messages"),
            amqp_args=ListenerAMQPArgs(
                exchange_name=ServiceUpdatesRMQOpts.exchange_name,
                exchange_type=ExchangeType.DIRECT,
                exchange_durable=True,
                queue_name=self.settings.service_updates_rk,
                queue_durable=True,
            ),
            channel=await self.amqp_conn.get_channel_from_pool(),
            incoming_message_type=IncomingServiceUpdateModel,
            callback=self._handle_service_update,
        )

    async def stop(self) -> None:
        await self.updates_listener.stop()
        await self.amqp_conn.stop()

    async def _handle_service_update(self, update: IncomingServiceUpdateModel) -> None:
        try:
            await call_handler(
                update=update.root,
                logger=self.logger,
                settings=self.settings,
                cacher=self.cacher,
                auth_srvc=self.auth_srvc,
                conn_srvc=self.conn_srvc,
                presence_srvc=self.presence_srvc,
                storage_srvc=self.storage_srvc,
                telegram_srvc=self.telegram_srvc,
                rabbitmq_publisher=self.rabbitmq_publisher,
                redis_publisher=self.redis_publisher,
            )

        except DropMessageError:
            raise

        except Exception as exc:
            self.logger.exception("Unhandled error occurred while processing service update", exc=exc)
