# pylint: disable=arguments-differ
from typing import Any, Type

from common.amocrm import AmoCRM
from common.amocrm.types import AmoLead
from common.email import EmailService
from src.admins.repos import AdminRepo
from src.agents.types import AgentEmail
from src.booking.repos import Booking, BookingRepo
from src.cities.repos import City, CityRepo
from src.notifications.services import GetEmailTemplateService
from src.users import constants
from src.users.entities import BaseUserService
from src.users.repos import Check, CheckTerm, CheckTermRepo, User, UserRoleRepo


class SendCheckAdminsEmailService(BaseUserService):
    """
    Отправляем письмо администратору о результатах проверки
    """

    def __init__(
        self,
        amocrm_class: Type[AmoCRM],
        admin_repo: Type[AdminRepo],
        booking_repo: Type[BookingRepo],
        email_class: Type[AgentEmail],
        get_email_template_service: GetEmailTemplateService,
        city_repo: Type[CityRepo],
        check_term_repo: Type[CheckTermRepo] = CheckTermRepo,
        user_role_repo: Type[UserRoleRepo] = UserRoleRepo,
    ):
        self.amocrm_class = amocrm_class
        self.admin_repo = admin_repo()
        self.booking_repo: BookingRepo = booking_repo()
        self.email_class: Type[AgentEmail] = email_class
        self.get_email_template_service: GetEmailTemplateService = get_email_template_service
        self.check_term_repo = check_term_repo()
        self.user_role_repo = user_role_repo()
        self.city_repo = city_repo()

        self.booking = None

    async def __call__(
        self,
        *,
        check: Check,
        mail_event_slug: str,
        data: dict[str, Any],
        additional_recipients_emails: list[str] | None = None,
    ):
        recipients: list[str] = await self._get_recipients(check)

        if additional_recipients_emails:
            recipients.extend(additional_recipients_emails)

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
        Получаем список получателей письма администраторов и РОПов.
        По умолчанию получатели - администраторы, которые привязаны к городу клиента и
        РОПы при нужном статусе.
        Получаем город клиента из сделки, по которой прошла проверка или из сделки в АМО.
        """
        if not check.amocrm_id:
            # Может не быть amocrm_id, если клиент уникальный и за ним нет сделок. Тогда письмо не отправляем
            return []

        booking: Booking = await self.booking_repo.retrieve(
            filters=dict(amocrm_id=check.amocrm_id, active=True),
            prefetch_fields=["project__city"],
        )
        self.booking = booking

        client_city: City = booking.project.city if booking and booking.project else None
        if not client_city:
            client_city = await self._get_client_city_from_amocrm(check.amocrm_id)
        if not client_city:
            return []

        admins: list[User] = await self.admin_repo.list(
            filters=dict(
                role=await self.user_role_repo.retrieve(filters=dict(slug=constants.UserType.ADMIN)),
                receive_admin_emails=True,
                users_cities__in=[client_city],
            ),
        )

        if await self.is_need_send_to_rop(check):
            rop_role = await self.user_role_repo.retrieve(filters=dict(slug=constants.UserType.ROP))
            if rop_role:
                admins += await self.admin_repo.list(
                    filters=dict(
                        role=rop_role,
                        users_cities__in=[client_city],
                    ),
                )

        recipients: list[str] = [admin.email for admin in admins if admin.email]

        return recipients

    async def is_need_send_to_rop(self, check) -> bool:
        filters = dict(uid=check.term_uid)
        check_term: CheckTerm = await self.check_term_repo.retrieve(filters=filters)
        if check_term:
            return check_term.send_rop_email

        return False

    async def _get_client_city_from_amocrm(self, amocrm_id) -> City:
        async with await self.amocrm_class() as amocrm:
            lead: AmoLead = await amocrm.fetch_lead(lead_id=amocrm_id)
            if lead.custom_fields_values:
                lead_custom_fields: dict = {field.field_id: field.values[0].value for field in
                                            lead.custom_fields_values}
                lead_city = lead_custom_fields.get(amocrm.city_field_id, None)
                if lead_city:
                    filters = dict(name=lead_city)
                    client_city: City = await self.city_repo.retrieve(filters=filters)

                    return client_city
