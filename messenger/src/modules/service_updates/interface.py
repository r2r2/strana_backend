from typing import Protocol

from src.core.common.rabbitmq import RabbitMQPublisherOptions
from src.core.common.utility import SupportsHealthCheck, SupportsLifespan


class UpdatesListenerProto(SupportsLifespan, SupportsHealthCheck, Protocol): ...


ServiceUpdatesRMQOpts = RabbitMQPublisherOptions(
    exchange_name="messenger",
    rk="service_updates",
    scope="service_updates",
)
