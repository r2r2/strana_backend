from pytz import UTC
from asyncio import Task
from datetime import datetime
from secrets import token_urlsafe
from typing import Callable, Any, Type

from ..entities import BaseRepresCase
from ..models import RequestSetPasswordModel
from ..repos import RepresRepo, User
from ..types import RepresSession, RepresHasher, RepresEmail
from ...users.loggers.wrappers import user_changes_logger
from ..exceptions import (
    RepresNotFoundError,
    RepresSamePasswordError,
    RepresPasswordTimeoutError,
    RepresChangePasswordError,
)


class SetPasswordCase(BaseRepresCase):
    """
    Установка пароля
    """

    template: str = "src/represes/templates/confirm_email.html"
    link: str = "https://{}/confirm/represes/confirm_email?q={}&p={}"

    def __init__(
        self,
        user_type: str,
        session: RepresSession,
        site_config: dict[str, Any],
        repres_repo: Type[RepresRepo],
        session_config: dict[str, Any],
        email_class: Type[RepresEmail],
        hasher: Callable[..., RepresHasher],
        token_creator: Callable[[int], str],
    ):
        self.hasher: RepresHasher = hasher()
        self.repres_repo: RepresRepo = repres_repo()
        self.repres_update = user_changes_logger(
            self.repres_repo.update, self, content="Обновление пароля представителя"
        )

        self.user_type: str = user_type
        self.session: RepresSession = session
        self.email_class: Type[RepresEmail] = email_class
        self.token_creator: Callable[[int], str] = token_creator

        self.site_host: str = site_config["site_host"]
        self.password_settable_key: str = session_config["password_settable_key"]
        self.password_reset_key: str = session_config["password_reset_key"]

    async def __call__(self, payload: RequestSetPasswordModel) -> User:
        data: dict[str, Any] = payload.dict()
        password: str = data["password"]
        is_contracted: bool = data["is_contracted"]
        repres_id: int = await self.session.get(
            self.password_settable_key
        ) or await self.session.get(self.password_reset_key)
        filters = dict(
            id=repres_id,
            is_approved=True,
            type=self.user_type,
        )
        repres: User = await self.repres_repo.retrieve(filters=filters)
        if not repres:
            raise RepresNotFoundError
        if repres.password and repres.one_time_password:
            raise RepresChangePasswordError
        if self.hasher.verify(password, repres.one_time_password or repres.password):
            raise RepresSamePasswordError
        if repres.one_time_password:
            if not repres.reset_time or repres.reset_time < datetime.now(tz=UTC):
                raise RepresPasswordTimeoutError
        data = dict(
            reset_time=None,
            one_time_password=None,
            is_contracted=is_contracted,
            email_token=token_urlsafe(32),
            password=self.hasher.hash(password),
        )
        repres: User = await self.repres_update(repres, data=data)
        token: str = self.token_creator(repres.id)
        await self._send_email(repres=repres, token=token)
        await self.session.pop(self.password_settable_key)
        await self.session.pop(self.password_reset_key)
        return repres

    async def _send_email(self, repres: User, token: str) -> Task:
        confirm_link: str = self.link.format(self.site_host, token, repres.email_token)
        email_options: dict[str, Any] = dict(
            topic="Подтверждение почты",
            template=self.template,
            recipients=[repres.email],
            context=dict(confirm_link=confirm_link),
        )
        email_service: RepresEmail = self.email_class(**email_options)
        return email_service.as_task()
