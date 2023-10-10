from asyncio import Task
from typing import Any, Type

from common.email import EmailService
from src.notifications.services import GetEmailTemplateService
from config import lk_admin_config
from src.agents.repos import AgentRepo, User
from src.notifications.repos import EventsSmsNotificationType

from ..services import GetEventNotificationTaskService
from ..entities import BaseEventCase
from ..models import RequestEventAdminModel
from ..repos import (Event, EventParticipantStatus, EventRepo)


class EventSendEmailFromAdminCase(BaseEventCase):
    """
    Кейс для отправки агенту письма при добавлении/удалении его к мероприятию админом.
    """

    mail_event_slug_agent_recorded = "admin_record_agent_on_event"
    mail_event_slug_agent_refused = "admin_refuse_agent_from_event"

    def __init__(
        self,
        event_repo: Type[EventRepo],
        agent_repo: Type[AgentRepo],
        email_class: Type[EmailService],
        get_email_template_service: GetEmailTemplateService,
        get_event_notification_task_service: GetEventNotificationTaskService,
    ) -> None:
        self.event_repo: EventRepo = event_repo()
        self.agent_repo: AgentRepo = agent_repo()
        self.email_class: Type[EmailService] = email_class
        self.get_email_template_service: GetEmailTemplateService = get_email_template_service
        self.get_event_notification_task_service: GetEventNotificationTaskService = get_event_notification_task_service

    async def __call__(
        self,
        payload: RequestEventAdminModel,
        data: str,
    ) -> None:
        if data != lk_admin_config["admin_export_key"]:
            return

        agent: User = await self.agent_repo.retrieve(
            filters=dict(id=payload.agent_id),
            related_fields=["agency"],
        )

        event: Event = await self.event_repo.retrieve(
            filters=dict(id=payload.event_id),
            prefetch_fields=["city", "participants"],
        )

        await self._send_email_to_agent(
            recipients=[agent.email],
            agent_participant_status=payload.agent_status,
            agent=agent,
            event=event,
        )

        await self.get_event_notification_task_service(
            event=event,
            user=agent,
            sms_event_type=EventsSmsNotificationType.BEFORE,
        )
        await self.get_event_notification_task_service(
            event=event,
            user=agent,
            sms_event_type=EventsSmsNotificationType.AFTER,
        )

    async def _send_email_to_agent(
            self,
            recipients: list[str],
            agent_participant_status: str,
            **context,
    ) -> Task:
        """
        Уведомляем агента о том, что он записан или удален администратором на мероприятие.
        @param recipients: list[str]
        @param context: Any (Контекст, который будет использоваться в шаблоне письма)
        @return: Task
        """
        if agent_participant_status == EventParticipantStatus.RECORDED:
            self.mail_event_slug = self.mail_event_slug_agent_recorded
        else:
            self.mail_event_slug = self.mail_event_slug_agent_refused

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
