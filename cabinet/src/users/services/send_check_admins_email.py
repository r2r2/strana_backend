# pylint: disable=arguments-differ
from typing import Any, Type

from common.email import EmailService
from common.unleash.unleash_client import UnleashAdapter
from config.feature_flags import FeatureFlags
from src.admins.repos import AdminRepo
from src.agents.types import AgentEmail
from src.booking.repos import Booking, BookingRepo
from src.cities.repos import City
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
        admin_repo: Type[AdminRepo],
        booking_repo: Type[BookingRepo],
        email_class: Type[AgentEmail],
        get_email_template_service: GetEmailTemplateService,
        check_term_repo: Type[CheckTermRepo] = CheckTermRepo,
        user_role_repo: Type[UserRoleRepo] = UserRoleRepo,
    ):
        self.admin_repo = admin_repo()
        self.booking_repo: BookingRepo = booking_repo()
        self.email_class: Type[AgentEmail] = email_class
        self.get_email_template_service: GetEmailTemplateService = get_email_template_service
        self.check_term_repo = check_term_repo()
        self.user_role_repo = user_role_repo()

    async def __call__(
            self,
            *,
            check: Check,
            mail_event_slug: str,
            data: dict[str, Any],
    ):
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
        Получаем список получателей письма администраторов и РОПов.
        По умолчанию получатели - администраторы, которые привязаны к городу клиента и
        РОПы при нужном статусе.
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
            filters=dict(
                role=await self.user_role_repo.retrieve(filters=dict(slug=constants.UserType.ADMIN)),
                receive_admin_emails=True,
                users_cities__in=[client_city],
            ),
        )
        unleash_client = UnleashAdapter()
        is_strana_lk_2257_enable = unleash_client.is_enabled(FeatureFlags.strana_lk_2257)

        if is_strana_lk_2257_enable:
            if await self.is_need_send_to_rop(check):
                rop_role = await self.user_role_repo.retrieve(filters=dict(slug=constants.UserType.ROP))
                admins += await self.admin_repo.list(
                    filters=dict(
                        role=rop_role,
                        receive_admin_emails=True,
                        users_cities__in=[client_city],
                    ),
                )

        recipients: list[str] = [admin.email for admin in admins if admin.email]

        return recipients

    async def is_need_send_to_rop(self, check):
        filters = dict(uid=check.term_uid)
        check_term: CheckTerm = await self.check_term_repo.retrieve(
            filters=filters,
            ordering='priority',
            related_fields=['unique_status'],
        )
        if check_term.priority in list(constants.CheckTermPriorityForSendToROP):
            return True

        return False
