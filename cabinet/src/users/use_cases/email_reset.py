from asyncio import Task
from secrets import token_urlsafe
from typing import Type, Any, Callable

from ..exceptions import UserNotFoundError
from ..models import RequestEmailResetModel
from ..repos import UserRepo, User
from ..entities import BaseUserCase
from ..types import UserEmail
from ..loggers.wrappers import user_changes_logger
from ..constants import UserType


class EmailResetCase(BaseUserCase):
    """
    Юзкейс для отправки ссылки для сброса пароля на почту пользователя.
    """

    agent_template: str = "src/agents/templates/reset_password.html"
    repres_template: str = "src/represes/templates/reset_password.html"
    admin_template: str = "src/admins/templates/reset_password.html"

    link: str = "https://{}/reset/admins/reset_password?q={}&p={}"

    def __init__(
        self,
        user_repo: Type[UserRepo],
        site_config: dict[str, Any],
        email_class: Type[UserEmail],
        token_creator: Callable[[int], str],
    ):
        self.user_repo: UserRepo = user_repo()
        self.user_update = user_changes_logger(
            self.user_repo.update, self, content="Создание токена для сброса пароля"
        )

        self.email_class: Type[UserEmail] = email_class
        self.token_creator: Callable[[int], str] = token_creator

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
        reset_link: str = self.link.format(self.site_host, token, user.discard_token)
        if user.type.value == "admin":
            template = self.admin_template
        elif user.type.value == "repres":
            template = self.repres_template
        else:
            template = self.agent_template

        email_options: dict[str, Any] = dict(
            topic="Сброс пароля",
            template=template,
            recipients=[user.email],
            context=dict(reset_link=reset_link),
        )
        email_service: UserEmail = self.email_class(**email_options)
        return email_service.as_task()
