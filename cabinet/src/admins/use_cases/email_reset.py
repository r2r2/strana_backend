from asyncio import Task
from secrets import token_urlsafe
from typing import Type, Any, Callable

from ..exceptions import AdminNotFoundError
from ..models import RequestEmailResetModel
from ..repos import AdminRepo, User
from ..entities import BaseAdminCase
from ..types import AdminEmail
from src.users.loggers.wrappers import user_changes_logger


class EmailResetCase(BaseAdminCase):
    """
    Ссылка для сброса
    """

    template: str = "src/admins/templates/reset_password.html"
    link: str = "https://{}/reset/admins/reset_password?q={}&p={}"

    def __init__(
        self,
        user_type: str,
        admin_repo: Type[AdminRepo],
        site_config: dict[str, Any],
        email_class: Type[AdminEmail],
        token_creator: Callable[[int], str],
    ):
        self.admin_repo: AdminRepo = admin_repo()
        self.admin_update = user_changes_logger(
            self.admin_repo.update, self, content="Создание токена для сброса пароля"
        )

        self.user_type: str = user_type
        self.email_class: Type[AdminEmail] = email_class
        self.token_creator: Callable[[int], str] = token_creator

        self.site_host: str = site_config["site_host"]

    async def __call__(self, payload: RequestEmailResetModel) -> User:
        data: dict[str, Any] = payload.dict()
        email: str = data["email"]
        filters: dict[str, Any] = dict(email__iexact=email, is_active=True, type=self.user_type)
        admin: User = await self.admin_repo.retrieve(filters=filters)
        if not admin:
            raise AdminNotFoundError
        token: str = self.token_creator(admin.id)
        data: dict[str, Any] = dict(discard_token=token_urlsafe(32))
        await self.admin_update(admin, data=data)
        await self._send_email(admin=admin, token=token)
        return admin

    async def _send_email(self, admin: User, token: str) -> Task:
        reset_link: str = self.link.format(self.site_host, token, admin.discard_token)
        email_options: dict[str, Any] = dict(
            topic="Сброс пароля",
            template=self.template,
            recipients=[admin.email],
            context=dict(reset_link=reset_link),
        )
        email_service: AdminEmail = self.email_class(**email_options)
        return email_service.as_task()
