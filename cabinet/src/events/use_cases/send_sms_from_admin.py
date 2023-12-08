import asyncio

import structlog

from src.events.entities import BaseEventCase
from src.events.exceptions import EventNotFoundError
from src.events.repos import EventRepo, Event
from src.events.services import SendingSmsToBrokerOnEventService
from src.notifications.exceptions import SMSTemplateNotFoundError, SMSTemplateNotActiveError
from src.notifications.repos import (
    EventsSmsNotificationRepo,
)


class SendSMSFromAdminCase(BaseEventCase):
    """
    Отправка СМС по кнопке из админки (таблица 8.1)
    """
    def __init__(
        self,
        event_repo: type[EventRepo],
        event_sms_notification_repo: type[EventsSmsNotificationRepo],
        sending_sms_to_broker: SendingSmsToBrokerOnEventService,
    ):
        self.event_repo: EventRepo = event_repo()
        self.event_sms_notification_repo: EventsSmsNotificationRepo = event_sms_notification_repo()
        self.sending_sms_to_broker: SendingSmsToBrokerOnEventService = sending_sms_to_broker

        self.logger: structlog.BoundLogger = structlog.get_logger(self.__class__.__name__)

    async def __call__(
        self,
        event_id: int,
    ) -> None:
        event: Event = await self.event_repo.retrieve(
            filters=dict(id=event_id),
            related_fields=["sms_template"],
            prefetch_fields=["participants__agent"],
        )
        self._validate_event(event=event)
        await self._process_event(event=event)

    async def _process_event(
        self,
        event: Event,
    ) -> None:
        for participant in event.participants:
            self.logger.info(f"Sending SMS for [{event=}] to [{participant.agent=}].")
            asyncio.create_task(
                self.sending_sms_to_broker(
                    event_id=event.id,
                    broker_id=participant.agent.id,
                    sms_event_slug=event.sms_template.sms_event_slug,
                )
            )

    def _validate_event(self, event: Event) -> None:
        if not event:
            raise EventNotFoundError

        if not event.sms_template:
            raise SMSTemplateNotFoundError

        if not event.sms_template.is_active:
            raise SMSTemplateNotActiveError
