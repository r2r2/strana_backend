import json
from typing import Any, Type

from aio_pika import Message
from aio_pika.abc import AbstractChannel, AbstractIncomingMessage
from boilerplates.rabbitmq import publish_message
from pydantic import TypeAdapter, ValidationError

from src.core.types import T


def parse_amqp_message(message: AbstractIncomingMessage, expected_type: Type[T]) -> T | None:
    decoded_body = message.body.decode(errors="replace")

    try:
        data = json.loads(decoded_body)
        return TypeAdapter(expected_type).validate_python(data)

    except ValidationError:
        return None

    except (json.JSONDecodeError, TypeError):
        return None


async def publish_amqp_message(
    *,
    message: Any,
    channel: AbstractChannel,
    exchange_name: str,
    routing_key: str,
    expiration: int | None = None,
) -> None:
    await publish_message(
        channel=channel,
        rk=routing_key,
        exchange_name=exchange_name,
        message=Message(
            json.dumps(message, ensure_ascii=False).encode(),
            content_type="application/json",
            expiration=expiration,
        ),
        create_exchange_with_memory_leak=False,
    )
