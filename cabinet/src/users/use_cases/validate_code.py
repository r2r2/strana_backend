from datetime import datetime, timedelta
from typing import Any, Callable, Type

from pytz import UTC
from src.users import services
from src.users.repos.notification_mute import (NotificationMuteRepo,
                                               RealIpUsersRepo)

from ...agents.types import AgentAmoCRM
from ...booking.tasks import import_bookings_task
from ..constants import UserType
from ..entities import BaseUserCase
from ..exceptions import (UserCodeTimeoutError, UserMaxCodeAttemptsError,
                          UserNotFoundError, UserWrongCodeError)
from ..loggers.wrappers import user_changes_logger
from ..models import RequestValidateCodeModel
from ..repos import User, UserRepo
from ..types import UserSession


class ValidateCodeCase(BaseUserCase):
    """
    Валидация кода
    """

    def __init__(
        self,
        session: UserSession,
        user_repo: Type[UserRepo],
        session_config: dict[str, Any],
        create_amocrm_contact_service: services.CreateContactService,
        token_creator: Callable[[int], dict[str, Any]],
        amocrm_class: Type[AgentAmoCRM],
        real_ip_repo: Type[RealIpUsersRepo],
        notification_mute_repo: Type[NotificationMuteRepo],
    ) -> None:
        self.user_repo: UserRepo = user_repo()
        self.user_update = user_changes_logger
        self.real_ip_repo = real_ip_repo()
        self.notification_mute_repo = notification_mute_repo()

        self.session: UserSession = session
        self.create_amocrm_contact_service: Any = create_amocrm_contact_service
        self.token_creator: Callable[[int], dict[str, Any]] = token_creator

        self.auth_key: str = session_config["auth_key"]
        self.auth_attempts_key: str = session_config["auth_attempts_key"]
        self.amocrm_class: Type[AgentAmoCRM] = amocrm_class
        self.import_bookings_task: Any = import_bookings_task

    async def __call__(self, payload: RequestValidateCodeModel, real_ip: str) -> dict[str, str]:
        data: dict[str, Any] = payload.dict()
        phone: str = data["phone"]
        filters: dict[str, Any] = dict(phone=phone, type=UserType.CLIENT)
        user: User = await self.user_repo.retrieve(filters=filters)
        auth_attempts: int = self.session.data.get(self.auth_attempts_key, 0)

        if auth_attempts >= 3:
            raise UserMaxCodeAttemptsError
        if user:
            time_valid: bool = user.code_time + timedelta(minutes=5) > datetime.now(tz=UTC)
            code_valid: bool = data["code"] == user.code and str(data["token"]) == str(user.token)

            if not time_valid:
                raise UserCodeTimeoutError
            if not code_valid:
                await self._incr_max_auth_attempts(auth_attempts)
                raise UserWrongCodeError
            if not user.auth_first_at:
                await self.user_update(
                    self.user_repo.update, self, content='Обновление времени авторизации клиента'
                )(user=user, data=dict(auth_first_at=datetime.now(tz=UTC)))
            await self.clear_notification_mute(phone=user.phone, real_ip=real_ip)
        else:
            raise UserNotFoundError

        if not user.is_imported:
            amocrm_id: int = await self.create_amocrm_contact_service(user=user)
            data: dict[str, Any] = dict(is_imported=True, amocrm_id=amocrm_id, is_active=True)
            await self.user_update(
                self.user_repo.update, self, content='Обновление данных не импортированного клиента'
            )(user=user, data=data)
        if not user.is_independent_client:
            await self.user_update(
                self.user_repo.update, self, content='Обновление данных зависимого клиента'
            )(user=user, data=dict(is_independent_client=True))
        token: dict[str, str] = self.token_creator(subject_type=user.type.value, subject=user.id)
        token["id"]: int = user.id
        token["role"]: str = user.type.value
        self.session[self.auth_key]: dict[str, str] = token
        await self.session.insert()
        self.import_bookings_task.delay(user_id=user.id)
        return token

    async def _incr_max_auth_attempts(self, auth_attempts: int):
        await self.session.set(
            key=self.auth_attempts_key,
            value=auth_attempts + 1,
            expire=self.session.auth_attempts_expire,
        )

    async def clear_notification_mute(self, phone: str, real_ip: str):
        """
        Очищаем реальных клиентов
        """
        notification_mute = await self.notification_mute_repo.retrieve(filters=dict(phone=phone))
        if notification_mute:
            await self.notification_mute_repo.delete(notification_mute)
        real_ip_obj = await self.real_ip_repo.retrieve(filters=dict(real_ip=real_ip, blocked=False))
        if real_ip_obj:
            await self.real_ip_repo.delete(real_ip_obj)
