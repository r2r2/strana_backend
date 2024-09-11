from datetime import timedelta
from typing import Generic, Protocol, TypeVar

from aio_pika import ExchangeType
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from src.core.common import ProtectedProperty, time_it
from src.core.common.rabbitmq import AMQPConnectionSettings, ConnectionHolder, publish_amqp_message
from src.core.common.utility import SupportsHealthCheck, SupportsLifespan
from src.core.logger import LoggerName, get_logger
from src.core.types import LoggerType


class RabbitMQPublisherOptions(BaseModel):
    exchange_name: str
    rk: str
    scope: str = ""


RabbitMQPublisherOptionsT = TypeVar("RabbitMQPublisherOptionsT", bound=RabbitMQPublisherOptions)


class ConcreteAMQPPublisherProto(Protocol):
    async def publish_delayed_update(self, update: BaseModel, delay: timedelta) -> None: ...
    async def publish_update(self, update: BaseModel) -> None: ...


class RabbitMQPublisherFactoryProto(SupportsLifespan, SupportsHealthCheck, Protocol):
    def __getitem__(self, item: RabbitMQPublisherOptions) -> ConcreteAMQPPublisherProto: ...


class RabbitMQPublisherSettings(BaseModel):
    amqp: AMQPConnectionSettings


class ConcreteAMQPPublisher(ConcreteAMQPPublisherProto):
    def __init__(
        self,
        logger: LoggerType,
        exchange_name: str,
        rk: str,
        scope: str,
        conn: ConnectionHolder,
        registered_delayed_exchanges: set[tuple[str, str]],
    ) -> None:
        self.logger = logger
        self.exchange_name = exchange_name
        self.rk = rk
        self.conn = conn
        self.scope = scope
        self.registered_delayed_exchanges: set[tuple[str, str]] = registered_delayed_exchanges

    async def publish_delayed_update(
        self,
        update: BaseModel,
        delay: timedelta,
    ) -> None:
        with time_it(self.logger, f"Delayed publish time ({self.scope}), delay: {delay.total_seconds()} sec."):
            async with self.conn.channel_pool.acquire() as channel:
                delayed_exchange_name = f"{self.exchange_name}_delayed"
                delayed_rk_name = f"{self.rk}_delayed"
                cache_pair = (self.exchange_name, self.rk)

                if cache_pair not in self.registered_delayed_exchanges:
                    await channel.declare_exchange(
                        name=delayed_exchange_name,
                        type=ExchangeType.DIRECT,
                        durable=True,
                    )
                    queue = await channel.declare_queue(
                        name=delayed_rk_name,
                        durable=True,
                        arguments={
                            "x-dead-letter-exchange": self.exchange_name,
                            "x-dead-letter-routing-key": self.rk,
                        },
                    )
                    await queue.bind(delayed_exchange_name, routing_key=delayed_rk_name)
                    self.registered_delayed_exchanges.add(cache_pair)

                await publish_amqp_message(
                    channel=channel,
                    exchange_name=delayed_exchange_name,
                    routing_key=delayed_rk_name,
                    message=jsonable_encoder(update),
                    expiration=int(delay.total_seconds()),
                )

    async def publish_update(
        self,
        update: BaseModel,
    ) -> None:
        with time_it(self.logger, f"Publish time ({self.scope})"):
            async with self.conn.channel_pool.acquire() as channel:
                await publish_amqp_message(
                    channel=channel,
                    exchange_name=self.exchange_name,
                    routing_key=self.rk,
                    message=jsonable_encoder(update),
                )


class RabbitMQPublisherFactory(RabbitMQPublisherFactoryProto, Generic[RabbitMQPublisherOptionsT]):
    conn = ProtectedProperty[ConnectionHolder]()

    def __init__(self, amqp_settings: AMQPConnectionSettings) -> None:
        self.logger = get_logger(LoggerName.RMQ_PUBLISHER)
        self.conn = ConnectionHolder(settings=amqp_settings, logger=self.logger.bind(subtype="connection"))
        self._registered_delayed_exchanges = set()

    async def health_check(self) -> bool:
        async with self.conn.channel_pool.acquire():
            return True

    async def start(self) -> None:
        await self.conn.start()

    async def stop(self) -> None:
        await self.conn.stop()

    def __getitem__(self, item: RabbitMQPublisherOptions) -> ConcreteAMQPPublisher:
        return ConcreteAMQPPublisher(
            logger=self.logger.bind(rk=item.rk),
            exchange_name=item.exchange_name,
            rk=item.rk,
            scope=item.scope,
            conn=self.conn,
            registered_delayed_exchanges=self._registered_delayed_exchanges,
        )
