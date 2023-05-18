from typing import Any, Type

from ..entities import BaseUserService
from ..repos import User
from ..types import UserAmoCRM


class UpdateContactService(BaseUserService):
    """
    Обновление пользователя в AmoCRM (экспорт).
    """

    def __init__(
        self,
        amocrm_class: Type[UserAmoCRM],
    ) -> None:
        self.amocrm_class: Type[UserAmoCRM] = amocrm_class

    async def __call__(
        self,
        user: User,
    ) -> None:
        async with await self.amocrm_class() as amocrm:
            await self._update_contact_data(user, amocrm)

    @staticmethod
    async def _update_contact_data(user: User, amocrm: UserAmoCRM):
        """
        Обновление данных контакта в АмоСРМ.
        """
        if user.patronymic:
            user_name = f"{user.surname} {user.name} {user.patronymic}"
        else:
            user_name = f"{user.surname} {user.name}"

        update_options: dict[str, Any] = dict(
            user_id=user.amocrm_id,
            user_name=user_name,
            user_email=user.email,
            user_phone=user.phone,
            user_company=user.agency.amocrm_id,
            user_birth_date=user.birth_date,
        )

        await amocrm.update_contact(**update_options)
