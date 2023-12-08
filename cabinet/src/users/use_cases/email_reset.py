from asyncio import Task
from secrets import token_urlsafe
from typing import Type, Any, Callable
from enum import StrEnum

from ..exceptions import UserNotFoundError
from ..models import RequestEmailResetModel
from ..repos import UserRepo, User
from ..entities import BaseUserCase
from ..types import UserEmail
from ..loggers.wrappers import user_changes_logger
from ..constants import UserType
from src.notifications.services import GetEmailTemplateService


class UserUrlType(StrEnum):
    ADMIN = 'admins'
    REPRES = 'represes'
    AGENT = 'agents'


class EmailResetCase(BaseUserCase):
    """
    Юзкейс для отправки ссылки для сброса пароля на почту пользователя.
    """
    agent_mail_event_slug = "agent_reset_password"
    repres_mail_event_slug = "repres_reset_password"
    admin_mail_event_slug = "admin_reset_password"

    link: str = "https://{}/api/{}/reset_password?q={}&p={}"

    def __init__(
        self,
        user_repo: Type[UserRepo],
        site_config: dict[str, Any],
        email_class: Type[UserEmail],
        token_creator: Callable[[int], str],
        get_email_template_service: GetEmailTemplateService,
    ):
        self.user_repo: UserRepo = user_repo()
        self.user_update = user_changes_logger(
            self.user_repo.update, self, content="Создание токена для сброса пароля"
        )

        self.email_class: Type[UserEmail] = email_class
        self.token_creator: Callable[[int], str] = token_creator
        self.get_email_template_service: GetEmailTemplateService = get_email_template_service

        self.site_host: str = site_config["site_host"]

    async def __call__(self, payload: RequestEmailResetModel) -> User:
        data: dict[str, Any] = payload.dict()
        email: str = data["email"]

        admin_query = self.user_repo.retrieve(filters=dict(email__iexact=email, type=UserType.ADMIN))
        repres_query = self.user_repo.retrieve(filters=dict(email__iexact=email, type=UserType.REPRES))
        agent_query = self.user_repo.retrieve(filters=dict(email__iexact=email, type=UserType.AGENT))

        user: User = await admin_query or await repres_query or await agent_query
        if not user:
            raise UserNotFoundError
        if user and user.type.value in ("agent", "repres") and not user.is_approved:
            raise UserNotFoundError

        token: str = self.token_creator(user.id)
        data: dict[str, Any] = dict(discard_token=token_urlsafe(32))
        await self.user_update(user, data=data)
        await self._send_email(user=user, token=token)
        return user

    async def _send_email(self, user: User, token: str) -> Task:
        if user.type.value == "admin":
            mail_event_slug = self.admin_mail_event_slug
            reset_link: str = self.link.format(self.site_host, UserUrlType.ADMIN.value, token, user.discard_token)
        elif user.type.value == "repres":
            mail_event_slug = self.repres_mail_event_slug
            reset_link: str = self.link.format(self.site_host, UserUrlType.REPRES.value, token, user.discard_token)
        else:
            mail_event_slug = self.agent_mail_event_slug
            reset_link: str = self.link.format(self.site_host, UserUrlType.AGENT.value, token, user.discard_token)

        email_notification_template = await self.get_email_template_service(
            mail_event_slug=mail_event_slug,
            context=dict(reset_link=reset_link),
        )

        if email_notification_template and email_notification_template.is_active:
            email_options: dict[str, Any] = dict(
                topic=email_notification_template.template_topic,
                content=email_notification_template.content,
                recipients=[user.email],
                lk_type=email_notification_template.lk_type.value,
                mail_event_slug=email_notification_template.mail_event_slug,
            )
            email_service: UserEmail = self.email_class(**email_options)
            return email_service.as_task()
