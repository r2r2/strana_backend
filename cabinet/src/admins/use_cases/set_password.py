from pytz import UTC
from datetime import datetime
from secrets import token_urlsafe
from typing import Callable, Any, Type

import structlog

from ..repos import AdminRepo, User
from ..entities import BaseAdminCase
from ..models import RequestSetPasswordModel
from ..types import AdminSession, AdminEmail, AdminHasher
from src.users.loggers.wrappers import user_changes_logger
from ..exceptions import (
    AdminNotFoundError,
    AdminChangePasswordError,
    AdminSamePasswordError,
    AdminPasswordTimeoutError,
)


class SetPasswordCase(BaseAdminCase):
    """
    Установка пароля
    """

    def __init__(
        self,
        user_type: str,
        session: AdminSession,
        site_config: dict[str, Any],
        admin_repo: Type[AdminRepo],
        session_config: dict[str, Any],
        email_class: Type[AdminEmail],
        hasher: Callable[..., AdminHasher],
    ):
        self.hasher: AdminHasher = hasher()
        self.admin_repo: AdminRepo = admin_repo()
        self.admin_update = user_changes_logger(
            self.admin_repo.update, self, content="Установка нового пароля"
        )

        self.user_type: str = user_type
        self.session: AdminSession = session
        self.email_class: Type[AdminEmail] = email_class

        self.site_host: str = site_config["site_host"]
        self.password_settable_key: str = session_config["password_settable_key"]
        self.password_reset_key: str = session_config["password_reset_key"]
        self.logger = structlog.getLogger('errors')

    async def __call__(self, payload: RequestSetPasswordModel) -> User:
        data: dict[str, Any] = payload.dict()
        password: str = data["password"]
        is_contracted: bool = data["is_contracted"]
        admin_id: int = await self.session.get(
            self.password_settable_key
        ) or await self.session.get(self.password_reset_key)
        filters = dict(
            id=admin_id,
            is_active=True,
            type=self.user_type,
        )
        admin: User = await self.admin_repo.retrieve(filters=filters)
        if not admin:
            self.logger.error(
                'Не удалось найти админа для смены пароля.',
                filters=filters,
                session=self.session.session_id
            )
            raise AdminNotFoundError
        if admin.password and admin.one_time_password:
            raise AdminChangePasswordError
        if self.hasher.verify(password, admin.one_time_password or admin.password):
            raise AdminSamePasswordError
        if admin.one_time_password:
            if not admin.reset_time or admin.reset_time < datetime.now(tz=UTC):
                raise AdminPasswordTimeoutError
        data = dict(
            reset_time=None,
            one_time_password=None,
            is_contracted=is_contracted,
            email_token=token_urlsafe(32),
            password=self.hasher.hash(password),
        )
        admin: User = await self.admin_update(admin, data=data)
        await self.session.pop(self.password_settable_key)
        await self.session.pop(self.password_reset_key)
        return admin
