from asyncio import Task
from secrets import token_urlsafe
from typing import Type, Any, Callable

from ..exceptions import RepresNotFoundError, RepresNotApprovedError
from ..models import RequestEmailResetModel
from ..repos import RepresRepo, User
from ..entities import BaseRepresCase
from ..types import RepresEmail
from ...users.loggers.wrappers import user_changes_logger


class EmailResetCase(BaseRepresCase):
    """
    Ссылка для сброса
    """

    template: str = "src/represes/templates/reset_password.html"
    link: str = "https://{}/reset/represes/reset_password?q={}&p={}"

    def __init__(
        self,
        user_type: str,
        repres_repo: Type[RepresRepo],
        site_config: dict[str, Any],
        email_class: Type[RepresEmail],
        token_creator: Callable[[int], str],
    ):
        self.repres_repo: RepresRepo = repres_repo()
        self.repres_update = user_changes_logger(
            self.repres_repo.update, self, content="Обновление данных представителя"
        )

        self.user_type: str = user_type
        self.email_class: Type[RepresEmail] = email_class
        self.token_creator: Callable[[int], str] = token_creator

        self.site_host: str = site_config["site_host"]

    async def __call__(self, payload: RequestEmailResetModel) -> User:
        data: dict[str, Any] = payload.dict()
        email: str = data["email"]
        filters: dict[str, Any] = dict(email__iexact=email, type=self.user_type)
        repres: User = await self.repres_repo.retrieve(filters=filters)
        if not repres:
            raise RepresNotFoundError
        if not repres.is_approved:
            raise RepresNotApprovedError
        token: str = self.token_creator(repres.id)
        data: dict[str, Any] = dict(discard_token=token_urlsafe(32))
        await self.repres_update(repres, data=data)
        await self._send_email(repres=repres, token=token)
        return repres

    async def _send_email(self, repres: User, token: str) -> Task:
        reset_link: str = self.link.format(self.site_host, token, repres.discard_token)
        email_options: dict[str, Any] = dict(
            topic="Сброс пароля",
            template=self.template,
            recipients=[repres.email],
            context=dict(reset_link=reset_link),
        )
        email_service: RepresEmail = self.email_class(**email_options)
        return email_service.as_task()
