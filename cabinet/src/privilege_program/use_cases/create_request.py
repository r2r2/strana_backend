from asyncio import Task

import structlog

from common.email import EmailService
from common.settings.repos import FeedbackSettingsRepo
from src.notifications.services import GetEmailTemplateService
from ..entities import BasePrivilegeServiceCase
from ..repos import PrivilegeRequest, PrivilegeRequestRepo
from ..models import CreatePrivilegeRequest


class CreateRequestCase(BasePrivilegeServiceCase):
    """
    Кейс создания заявки
    """

    privilege_program_notification_slug: str = "privilege_program_notification"

    def __init__(
        self,
        request_repo: type[PrivilegeRequestRepo],
        feedback_settings_repo: type[FeedbackSettingsRepo],
        email_class: type[EmailService],
        get_email_template_service: GetEmailTemplateService,
    ) -> None:
        self.request_repo: PrivilegeRequestRepo = request_repo()
        self.feedback_settings_repo: FeedbackSettingsRepo = feedback_settings_repo()
        self.email_class: type[EmailService] = email_class
        self.get_email_template_service: GetEmailTemplateService = (
            get_email_template_service
        )
        self.logger = structlog.getLogger(__name__)

    async def __call__(self, user_id: int, payload: CreatePrivilegeRequest) -> PrivilegeRequest:
        request_data: dict = payload.dict(exclude_none=True)
        request_data.update(user_id=user_id)
        created_request: PrivilegeRequest = await self.request_repo.create(data=request_data)
        if created_request:
            await self.send_email_notify(created_request=created_request)
        return created_request

    async def send_email_notify(self, created_request: PrivilegeRequest) -> Task | None:
        """
        Уведомление о создании заявки в Программу привилегий
        """
        email_notification_template = await self.get_email_template_service(
            mail_event_slug=self.privilege_program_notification_slug,
            context=dict(
                full_name=created_request.full_name,
                phone=created_request.phone,
                email=created_request.email,
                question=created_request.question,
            ),
        )
        recipients = await self.feedback_settings_repo.list().values_list(
            "privilege_emails__email", flat=True
        )
        if recipients == [None]:
            self.logger.warning("Получатели не найдены")
            return

        if email_notification_template and email_notification_template.is_active:
            email_options: dict = dict(
                topic=email_notification_template.template_topic,
                content=email_notification_template.content,
                lk_type=email_notification_template.lk_type.value,
                mail_event_slug=email_notification_template.mail_event_slug,
                recipients=recipients,
            )
            email_service: EmailService = self.email_class(**email_options)
            return email_service.as_task()
        else:
            self.logger.warning("Нет активного шаблона для уведомления")
