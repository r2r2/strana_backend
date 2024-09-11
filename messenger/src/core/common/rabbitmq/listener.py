import asyncio
from dataclasses import dataclass, field
from functools import partial
from typing import Any, Awaitable, Callable, Generic, Type

from aio_pika.abc import (
    AbstractChannel,
    AbstractIncomingMessage,
    AbstractQueue,
    ConsumerTag,
)
from aio_pika.exchange import ExchangeType

from src.core.common import time_it
from src.core.common.rabbitmq.exceptions import DropMessageError
from src.core.common.rabbitmq.helpers import parse_amqp_message
from src.core.types import LoggerType, T


@dataclass(kw_only=True, repr=True)
class ListenerAMQPArgs:
    exchange_name: str
    exchange_type: ExchangeType | None = field(default=None)
    exchange_durable: bool | None = field(default=None)
    queue_name: str
    queue_durable: bool

    def __post_init__(self) -> None:
        if self.exchange_type and not self.exchange_durable:
            raise ValueError("Exchange type is set, but exchange durability is not")


class QueueListener(Generic[T]):
    @staticmethod
    async def _callback(
        message: AbstractIncomingMessage,
        expected_type: Type[T],
        callback: Callable[[T], Awaitable[Any]],
        logger: LoggerType,
    ) -> None:
        with time_it(logger, "Handle time"):
            decoded = parse_amqp_message(message, expected_type=expected_type)
            if not decoded:
                logger.error(f"Incorrect message type: {message.body!r}")
                await message.reject(requeue=False)
                return

            try:
                await callback(decoded)

            except asyncio.CancelledError:
                # Incoming message processing has been cancelled, skip
                await message.reject(requeue=True)

            except DropMessageError:
                await message.reject(requeue=False)

            except Exception as exc:  # pylint: disable=broad-except
                logger.error(f"Error when processing an incoming message: {type(exc).__name__}]", exc_info=True)
                await message.reject(requeue=False)

            else:
                await message.ack()

    @classmethod
    async def create(
        cls,
        logger: LoggerType,
        channel: AbstractChannel,
        amqp_args: ListenerAMQPArgs,
        incoming_message_type: Type[T],
        callback: Callable[[T], Awaitable[Any]],
        prefetch_count: int = 1,
    ) -> "QueueListener[T]":
        if amqp_args.exchange_type and amqp_args.exchange_durable:
            exchange = await channel.declare_exchange(
                amqp_args.exchange_name,
                type=amqp_args.exchange_type,
                durable=amqp_args.exchange_durable,
            )
        else:
            exchange = await channel.get_exchange(amqp_args.exchange_name)

        await channel.set_qos(prefetch_count=prefetch_count)
        queue = await channel.declare_queue(name=amqp_args.queue_name, durable=amqp_args.queue_durable)
        await queue.bind(exchange)
        consumer_tag = await queue.consume(
            callback=partial(cls._callback, expected_type=incoming_message_type, callback=callback, logger=logger),
        )
        instance = cls(channel=channel, consumer_tag=consumer_tag, queue=queue, logger=logger)
        instance._set_is_running()
        return instance

    def __init__(
        self,
        logger: LoggerType,
        channel: AbstractChannel,
        queue: AbstractQueue,
        consumer_tag: ConsumerTag,
    ) -> None:
        self._consumer_tag = consumer_tag
        self._channel = channel
        self._queue = queue
        self._is_running = False
        self.logger = logger

    @property
    def is_running(self) -> bool:
        return self._is_running

    def _set_is_running(self) -> None:
        self._is_running = True

    async def stop(self) -> AbstractChannel:
        await self._queue.cancel(self._consumer_tag)
        self._is_running = False
        return self._channel
