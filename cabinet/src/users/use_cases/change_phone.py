from datetime import datetime, timedelta
from typing import Any, Type

from pytz import UTC

from ..entities import BaseUserCase
from ..exceptions import (UserChangePhoneError, UserCodeTimeoutError,
                          UserPhoneTakenError, UserSamePhoneError,
                          UserWrongCodeError)
from ..models import RequestChangePhoneModel
from ..repos import User, UserRepo
from ..types import UserAmoCRM
from ..loggers.wrappers import user_changes_logger


class ChangePhoneCase(BaseUserCase):
    """
    Смена телефона
    """

    def __init__(self, user_repo: Type[UserRepo], amocrm_class: Type[UserAmoCRM]) -> None:
        self.user_repo: UserRepo = user_repo()

        self.amocrm_class: Type[UserAmoCRM] = amocrm_class
        self.user_update = user_changes_logger(self.user_repo.update, self, content="Смена номера телефона")
        self.user_delete = user_changes_logger(self.user_repo.delete, self, content="Удаление пользователя")

    async def __call__(self, user_id: int, payload: RequestChangePhoneModel) -> User:
        data: dict[str, Any] = payload.dict()
        phone: str = data.pop("phone")
        filters: dict[str, Any] = dict(phone=phone)
        user: User = await self.user_repo.retrieve(filters=filters)
        if not user:
            raise UserChangePhoneError
        if int(user.id) == int(user_id):
            raise UserSamePhoneError
        if user.is_imported:
            raise UserPhoneTakenError

        time_valid: bool = user.code_time and user.code_time + timedelta(
            minutes=5
        ) > datetime.now(tz=UTC)
        code_valid: bool = (
            user.code
            and user.token
            and data["code"] == user.code
            and str(data["token"]) == str(user.token)
        )
        if not time_valid:
            raise UserCodeTimeoutError
        if not code_valid:
            raise UserWrongCodeError
        await self.user_repo.delete(user)

        filters: dict[str, Any] = dict(id=user_id)
        user: User = await self.user_repo.retrieve(filters=filters)
        data: dict[str, Any] = dict(phone=phone)
        await self.user_update(user=user, data=data)
        await self._amocrm_update(user=user)
        return user

    async def _amocrm_update(self, user: User):
        """
        Обновление контакта в амо
        """
        async with await self.amocrm_class() as amocrm:
            contact_options: dict[str, Any] = dict(
                user_phone=user.phone,
                user_email=user.email,
                user_id=user.amocrm_id,
                user_birth_date=user.birth_date,
                user_name=f"{user.surname} {user.name} {user.patronymic}",
                user_passport=f"{user.passport_series} {user.passport_number}",
            )
            await amocrm.update_contact(**contact_options)
