# pylint: disable=arguments-differ
from typing import Type, Any

from common.email import EmailService
from src.booking.repos import Booking, BookingRepo
from src.admins.repos import AdminRepo
from src.agents.types import AgentEmail
from src.cities.repos import City
from src.users.repos import Check, User
from src.notifications.services import GetEmailTemplateService
from ..entities import BaseUserService


class SendCheckAdminsEmailService(BaseUserService):
    """
    Отправляем письмо администратору о результатах проверки
    """

    def __init__(
        self,
        admin_repo: Type[AdminRepo],
        booking_repo: Type[BookingRepo],
        email_class: Type[AgentEmail],
        get_email_template_service: GetEmailTemplateService,
    ):
        self.admin_repo = admin_repo()
        self.booking_repo: BookingRepo = booking_repo()
        self.email_class: Type[AgentEmail] = email_class
        self.get_email_template_service: GetEmailTemplateService = get_email_template_service

    async def __call__(self, *, check: Check, mail_event_slug: str, data: dict[str, Any]):
        recipients: list[str] = await self._get_recipients(check)

        email_notification_template = await self.get_email_template_service(
            mail_event_slug=mail_event_slug,
            context=data,
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

    async def _get_recipients(self, check: Check) -> list[str]:
        """
        Получаем список получателей письма администраторов
        По умолчанию получатели - администраторы, которые привязаны к городу клиента
        Получаем город клиента из сделки, по которой прошла проверка.
        """
        if not check.amocrm_id:
            # Может не быть amocrm_id, если клиент уникальный и за ним нет сделок. Тогда письмо не отправляем
            return []

        booking: Booking = await self.booking_repo.retrieve(
            filters=dict(amocrm_id=check.amocrm_id, active=True),
            prefetch_fields=["project__city"],
        )
        client_city: City = booking.project.city if booking and booking.project else None
        if not client_city:
            # Если у сделки нет проекта, то как найти город клиента?
            return []

        admins: list[User] = await self.admin_repo.list(
            filters=dict(receive_admin_emails=True, users_cities__in=[client_city]),
        )

        recipients: list[str] = [admin.email for admin in admins if admin.email]

        return recipients
