import datetime
from asyncio import Task
from http import HTTPStatus
from typing import Any, Type

from common.email import EmailService
from fastapi import HTTPException
from pytz import UTC
from src.agents.repos import AgentRepo, User
from src.notifications.services import GetEmailTemplateService
from src.users.constants import UserType

from ..entities import BaseEventCase
from ..exceptions import (AgentAlreadySignupEventError,
                          EventHasAlreadyEndedError, EventHasNoPlacesError,
                          EventNotFoundError)
from ..repos import (Event, EventParticipantRepo, EventParticipantStatus,
                     EventRepo, EventType)


class EventAgentRecordCase(BaseEventCase):
    """
    Кейс для записи агента на мероприятие.
    """

    mail_event_slug = "agent_signup_on_event"

    def __init__(
        self,
        event_repo: Type[EventRepo],
        event_participant_repo: Type[EventParticipantRepo],
        agent_repo: Type[AgentRepo],
        email_class: Type[EmailService],
        get_email_template_service: GetEmailTemplateService,
    ) -> None:
        self.event_repo: EventRepo = event_repo()
        self.event_participant_repo: EventParticipantRepo = event_participant_repo()
        self.agent_repo: AgentRepo = agent_repo()
        self.email_class: Type[EmailService] = email_class
        self.get_email_template_service: GetEmailTemplateService = get_email_template_service

    async def __call__(
        self,
        event_id: int,
        user_id: int,
    ) -> None:
        user: User = await self.agent_repo.retrieve(
            filters=dict(id=user_id),
            related_fields=["agency", "maintained"],
        )

        if user.type not in [UserType.AGENT, UserType.REPRES]:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )

        filters = dict(id=event_id, is_active=True)

        if user.type == UserType.AGENT:
            q_filters = [self.event_repo.q_builder(
                or_filters=[
                    dict(type=EventType.ONLINE),
                    dict(type=EventType.OFFLINE, show_in_all_cities=True),
                    dict(type=EventType.OFFLINE, city__name=user.agency.city),
                ]
            )]
        else:
            q_filters = [self.event_repo.q_builder(
                or_filters=[
                    dict(type=EventType.ONLINE),
                    dict(type=EventType.OFFLINE, show_in_all_cities=True),
                    dict(type=EventType.OFFLINE, city__name=user.maintained.city),
                ]
            )]

        agent_exist_in_participants_qs = self.event_participant_repo.list(
            filters=dict(
                event_id=self.event_repo.a_builder.build_outer("id"),
                agent_id=user.id,
                status=EventParticipantStatus.RECORDED,
            )
        )
        participants_count_qs = self.event_participant_repo.list(
            filters=dict(
                event_id=self.event_repo.a_builder.build_outer("id"),
                status=EventParticipantStatus.RECORDED,
            )
        )
        event: Event = await self.event_repo.retrieve(
            filters=filters,
            q_filters=q_filters,
            prefetch_fields=["city", "participants"],
            annotations=dict(
                agent_recorded=self.event_repo.a_builder.build_exists(agent_exist_in_participants_qs),
                participants_count=self.event_repo.a_builder.build_scount(participants_count_qs),
            ),
        )
        if not event:
            raise EventNotFoundError

        if event.agent_recorded:
            raise AgentAlreadySignupEventError

        if event.max_participants_number and event.max_participants_number <= event.participants_count:
            raise EventHasNoPlacesError

        current_time = datetime.datetime.now(tz=UTC)
        if (event.record_date_end and event.record_date_end < current_time) or (
            event.meeting_date_start < current_time
        ):
            raise EventHasAlreadyEndedError

        await self.event_participant_repo.update_or_create(
            filters=dict(
                agent_id=user.id,
                event_id=event.id,
            ),
            data=dict(
                fio=f"{user.surname} {user.name} {user.patronymic}",
                phone=user.phone,
                status=EventParticipantStatus.RECORDED,
            )
        )

        event.agent_recorded = True
        event.participants_count = event.participants_count + 1

        await self._send_email_to_agent(
            recipients=[user.email],
            agent=user,
            event=event,
        )

        return event

    async def _send_email_to_agent(
        self,
        recipients: list[str],
        **context,
    ) -> Task:
        """
        Уведомляем агента о том, что он записался на мероприятие.
        @param recipients: list[str]
        @param context: Any (Контекст, который будет использоваться в шаблоне письма)
        @return: Task
        """
        email_notification_template = await self.get_email_template_service(
            mail_event_slug=self.mail_event_slug,
            context=context,
        )

        if email_notification_template and email_notification_template.is_active:
            email_options: dict[str, Any] = dict(
                topic=email_notification_template.template_topic,
                content=email_notification_template.content,
                recipients=recipients,
                lk_type=email_notification_template.lk_type.value,
                mail_event_slug=email_notification_template.mail_event_slug,
            )
            email_service: EmailService = self.email_class(**email_options)

            return email_service.as_task()
