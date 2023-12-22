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
from src.notifications.services import GetEmailTemplateService
from common.schemas import UrlEncodeDTO
from common.utils import generate_notify_url


class SetPasswordCase(BaseRepresCase):
    """
    Установка пароля
    """

    mail_event_slug = "repres_confirm_email"
    link: str = "https://{}/confirm/represes/confirm_email?q={}&p={}"
    link_route_template: str = "/confirm/represes/confirm_email"

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
        get_email_template_service: GetEmailTemplateService,
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

        self.get_email_template_service: GetEmailTemplateService = get_email_template_service

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
        url_data: dict[str, Any] = dict(
            host=self.site_host,
            route_template=self.link_route_template,
            query_params=dict(
                q=token,
                p=repres.email_token,
            )
        )
        url_dto: UrlEncodeDTO = UrlEncodeDTO(**url_data)
        confirm_link: str = generate_notify_url(url_dto=url_dto)
        email_notification_template = await self.get_email_template_service(
            mail_event_slug=self.mail_event_slug,
            context=dict(confirm_link=confirm_link),
        )

        if email_notification_template and email_notification_template.is_active:
            email_options: dict[str, Any] = dict(
                topic=email_notification_template.template_topic,
                content=email_notification_template.content,
                recipients=[repres.email],
                lk_type=email_notification_template.lk_type.value,
                mail_event_slug=email_notification_template.mail_event_slug,
            )
            email_service: RepresEmail = self.email_class(**email_options)
            return email_service.as_task()
