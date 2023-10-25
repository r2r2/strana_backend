import structlog

from typing import Type, Any

from common.email import EmailService
from src.notifications.services import GetEmailTemplateService
from ..models import SendingTestEmailModel
from ..entities import BaseNotificationCase


class SendingTestEmailCase(BaseNotificationCase):
    """
    Юзкейс запроса тестового апи для отправки писем (отладка шаблонов).
    """

    def __init__(
        self,
        email_class: Type[EmailService],
        get_email_template_service: GetEmailTemplateService,
    ):
        self.email_class: Type[EmailService] = email_class
        self.get_email_template_service: GetEmailTemplateService = get_email_template_service
        self.logger = structlog.get_logger(__name__)

    async def __call__(self, payload: SendingTestEmailModel) -> None:
        email_notification_template = await self.get_email_template_service(
            mail_event_slug=payload.slug,
            context=payload.context,
        )
        if not email_notification_template:
            self.logger.error("Не найден шаблон письма")
        else:
            self.logger.info(f"Заголовок письма - {email_notification_template.template_topic}")
            self.logger.info(f"Текст письма - {email_notification_template.content}")

        if email_notification_template and email_notification_template.is_active:
            email_options: dict[str, Any] = dict(
                topic=email_notification_template.template_topic,
                content=email_notification_template.content,
                recipients=payload.recipients,
                lk_type=email_notification_template.lk_type.value,
                mail_event_slug=email_notification_template.mail_event_slug,
            )

            email_service: EmailService = self.email_class(**email_options)
            email_service.as_task()
