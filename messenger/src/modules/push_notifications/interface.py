from datetime import datetime
from typing import Protocol

from pydantic import BaseModel, Field
from sl_messenger_protobuf.notifications_pb2 import PushNotificationContent
from web_pusher import ClientCredentials
from web_pusher.enums import Urgency

from src.core.common.rabbitmq import RabbitMQPublisherOptions
from src.core.common.utility import SupportsHealthCheck, SupportsLifespan
from src.modules.service_updates.entities import MessageSentToChat, TicketCreated, TicketStatusChanged
from src.providers.time import datetime_now

SourceEventType = MessageSentToChat | TicketCreated | TicketStatusChanged


class SendPushQueueMessage(BaseModel):
    source_event: SourceEventType = Field(..., discriminator="type")
    created_at: datetime = Field(default_factory=datetime_now)


class PushNotificationsListenerProto(SupportsLifespan, SupportsHealthCheck, Protocol): ...


class PushNotificationsSenderProto(SupportsLifespan, Protocol):
    async def send_notification(
        self,
        *,
        message: PushNotificationContent,
        client_credentials: ClientCredentials,
        ttl: int,
        urgency: Urgency,
        topic: str | None = None,
    ) -> None: ...


class PushNotificationEventsPublisherProto(SupportsLifespan, SupportsHealthCheck, Protocol):
    async def publish_update(self, update: SendPushQueueMessage) -> None: ...


PushNotificationsRMQOpts = RabbitMQPublisherOptions(
    exchange_name="messenger",
    rk="push_notifications",
    scope="push_notifications",
)
