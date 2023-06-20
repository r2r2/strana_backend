from copy import copy
from datetime import datetime, timedelta
from typing import Any, Optional, Type

from common.email.repos import LogEmailRepo
from common.messages.repos import LogSmsRepo
from jinja2 import Template
from tortoise import Tortoise

from .entities import BaseNotificationService
from .repos import (EmailTemplate, EmailTemplateRepo, SmsTemplate,
                    SmsTemplateRepo)


class CleanLogsNotificationService(BaseNotificationService):
    """
    Сервис очистки логов отправленных писем и смс старше 3 дней.
    """
    def __init__(
        self,
        log_email_repo: Type[LogEmailRepo],
        log_sms_repo: Type[LogSmsRepo],
        orm_class: Type[Tortoise],
        orm_config: dict,
    ) -> None:
        self.log_email_repo: LogEmailRepo = log_email_repo()
        self.log_sms_repo: LogSmsRepo = log_sms_repo()
        self.orm_class = orm_class
        self.orm_config = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

    async def __call__(self, days: int):
        threshold: datetime = datetime.now() - timedelta(days=days)
        clean_logs_filters: dict = dict(created_at__lte=threshold)
        await self.log_email_repo.list(filters=clean_logs_filters).delete()
        await self.log_sms_repo.list(filters=clean_logs_filters).delete()


class GetEmailTemplateService(BaseNotificationService):
    """
    Получаем шаблон письма из базы по слагу.
    """

    def __init__(
        self,
        email_template_repo: Type[EmailTemplateRepo],
    ) -> None:
        self.email_template_repo: EmailTemplateRepo = email_template_repo()

    async def __call__(
        self,
        mail_event_slug: str,
        context: Optional[dict[Any]] = None,
    ) -> Optional[EmailTemplate]:
        email_template = await self.email_template_repo.retrieve(
            filters=dict(mail_event_slug=mail_event_slug)
        )
        if email_template and context:
            rendered_content = await Template(email_template.template_text, enable_async=True).render_async(**context)
            email_template.content = rendered_content

        return email_template


class GetSmsTemplateService(BaseNotificationService):
    """
    Получаем шаблон смс из базы по слагу.
    """

    def __init__(
        self,
        sms_template_repo: Type[SmsTemplateRepo],
    ) -> None:
        self.sms_template_repo: SmsTemplateRepo = sms_template_repo()

    async def __call__(
        self,
        sms_event_slug: str,
    ) -> Optional[SmsTemplate]:
        sms_template = await self.sms_template_repo.retrieve(
            filters=dict(sms_event_slug=sms_event_slug)
        )

        return sms_template
