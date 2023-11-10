import datetime
from asyncio import Task
from typing import Any, Type
from copy import copy

from tortoise import Tortoise

from common.messages import SmsService
from src.users.repos import UserRepo, User
from src.notifications.services import GetSmsTemplateService

from ..entities import BaseEventCase
from ..repos import (
    Event,
    EventType,
    EventParticipantRepo,
    EventParticipantStatus,
    EventRepo,
)


class SendingSmsToBrokerOnEventService(BaseEventCase):
    """
    Сервис отправки смс уведомлений брокерам, записанным на мероприятие.
    """

    def __init__(
        self,
        event_repo: Type[EventRepo],
        event_participant_repo: Type[EventParticipantRepo],
        user_repo: Type[UserRepo],
        sms_class: Type[SmsService],
        get_sms_template_service: GetSmsTemplateService,
        orm_class: Type[Tortoise],
        orm_config: dict | None,
    ) -> None:
        self.event_repo: EventRepo = event_repo()
        self.event_participant_repo: EventParticipantRepo = event_participant_repo()
        self.user_repo: UserRepo = user_repo()
        self.sms_class: Type[SmsService] = sms_class
        self.get_sms_template_service: GetSmsTemplateService = get_sms_template_service

        self.orm_class = orm_class
        self.orm_config = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

    async def __call__(
        self,
        event_id: int,
        broker_id: int,
        sms_event_slug: str,
    ) -> None:
        broker: User = await self.user_repo.retrieve(filters=dict(id=broker_id))
        if not broker:
            return

        agent_exist_in_participants_qs = self.event_participant_repo.list(
            filters=dict(
                event_id=self.event_repo.a_builder.build_outer("id"),
                agent_id=broker.id,
                status=EventParticipantStatus.RECORDED,
            )
        )
        event: Event = await self.event_repo.retrieve(
            filters=dict(id=event_id),
            related_fields=["city"],
            annotations=dict(
                agent_recorded=self.event_repo.a_builder.build_exists(agent_exist_in_participants_qs),
            ),
        )

        if event and event.agent_recorded:
            await self._send_sms_to_broker(
                user=broker,
                sms_event_slug=sms_event_slug,
                event=event,
            )

    async def _send_sms_to_broker(self, user: User, sms_event_slug: str, event: Event) -> Task:
        """
        Отправка смс сообщений брокеру.
        """

        sms_notification_template = await self.get_sms_template_service(
            sms_event_slug=sms_event_slug,
        )
        if sms_notification_template and sms_notification_template.is_active:
            if event.type == EventType.ONLINE:
                broker_event_message = sms_notification_template.template_text.format(
                    event_date=(event.meeting_date_start + datetime.timedelta(hours=3)).date().strftime("%m.%d.%Y"),
                    event_time=(event.meeting_date_start + datetime.timedelta(hours=3)).time().strftime("%H.%M"),
                    event_online_link=event.link,
                )
            else:
                timezone_offset = event.city.timezone_offset if event.city else 0
                broker_event_message = sms_notification_template.template_text.format(
                    event_date=(event.meeting_date_start + datetime.timedelta(hours=timezone_offset)).date(),
                    event_time=(event.meeting_date_start + datetime.timedelta(hours=timezone_offset)).time(),
                    event_offline_address=event.address,
                    event_city=event.city.name if event.city else None,
                )

            sms_options: dict[str, Any] = dict(
                phone=user.phone,
                message=broker_event_message,
                lk_type=sms_notification_template.lk_type.value,
                sms_event_slug=sms_notification_template.sms_event_slug,
            )
            sms_service: SmsService = self.sms_class(**sms_options)
            return sms_service.as_task()
