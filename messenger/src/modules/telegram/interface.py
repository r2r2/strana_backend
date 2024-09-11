from typing import Protocol

from src.core.common.utility import SupportsLifespan

from .entities import NewTicketTgNotificationPayload

SupportedMessages = NewTicketTgNotificationPayload


class TelegramServiceProto(SupportsLifespan, Protocol):
    def send_message(self, message: SupportedMessages) -> None: ...
