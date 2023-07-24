from asyncio import Task
from typing import Any, Optional, Type

from config import site_config

from common.email import EmailService
from src.agents.types import AgentEmail

from ..entities import BaseAgencyCase
from ..models.superuser_additional_notify_agency_email import RequestAdditionalNotifyAgencyEmailModel
from ..repos import Agency, AgencyRepo
from ..exceptions import InvalidAdminDataError
from src.notifications.services import GetEmailTemplateService


class SuperuserAdditionalNotifyAgencyEmailCase(BaseAgencyCase):
    """
    Отправка писем представителям агентов при создании ДС в админке.
    """
    mail_event_slug = "create_additional_agreement"
    link = "https://{}/documents"

    def __init__(
        self,
        email_class: Type[AgentEmail],
        agency_repo: Type[AgencyRepo],
        get_email_template_service: GetEmailTemplateService,
        lk_admin_config: dict[str, Any],

    ) -> None:
        self.agency_repo: AgencyRepo = agency_repo()
        self.email_class: Type[AgentEmail] = email_class
        self.get_email_template_service: GetEmailTemplateService = get_email_template_service
        self.admin_export_key: str = lk_admin_config["admin_export_key"]

    async def __call__(
        self,
        data: str,
        payload=RequestAdditionalNotifyAgencyEmailModel,
    ) -> None:
        if data != self.admin_export_key:
            raise InvalidAdminDataError

        for agency_data in payload:
            agency: Optional[Agency] = await self.agency_repo.retrieve(
                filters=dict(id=agency_data.agency_id),
                related_fields=["maintainer"]
            )
            if not agency:
                continue

            project_names = agency_data.project_names

            if agency.maintainer and agency.maintainer.email and project_names:
                await self._send_repres_email(
                    recipients=[agency.maintainer.email],
                    project_names=project_names,
                    link=self.link.format(site_config["broker_site_host"]),
                )

    async def _send_repres_email(
        self,
        recipients: list[str],
        **context
    ) -> Task:
        """
        Уведомляем всех представителей агентств о новых дополнительных соглашениях.
        @param recipients: list[str]
        @param context: Any (Контекст, который будет использоваться в шаблоне письма)
        @return: Task
        """
        email_notification_template = await self.get_email_template_service(
            mail_event_slug=self.mail_event_slug,
            context=context,
        )

        if email_notification_template and email_notification_template.is_active:
            project_names = context.get("project_names")
            topic = email_notification_template.template_topic.format(project_names=', '.join(project_names))

            email_options: dict[str, Any] = dict(
                topic=topic,
                content=email_notification_template.content,
                recipients=recipients,
                lk_type=email_notification_template.lk_type.value,
                mail_event_slug=email_notification_template.mail_event_slug,
            )
            email_service: EmailService = self.email_class(**email_options)

            return email_service.as_task()
