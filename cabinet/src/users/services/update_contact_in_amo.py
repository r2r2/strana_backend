from typing import Any, Type
from copy import copy

from tortoise import Tortoise

from ..entities import BaseUserService
from ..repos import User, UserRepo
from ..types import UserAmoCRM


class UpdateContactService(BaseUserService):
    """
    Обновление пользователя в AmoCRM (экспорт).
    """

    def __init__(
        self,
        amocrm_class: Type[UserAmoCRM],
        user_repo: Type[UserRepo],
        orm_class: Type[Tortoise],
        orm_config: dict,
    ) -> None:
        self.amocrm_class: Type[UserAmoCRM] = amocrm_class
        self.user_repo: UserRepo = user_repo()
        self.orm_class = orm_class
        self.orm_config = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

    async def __call__(
        self,
        user_id: int,
    ) -> None:
        user: User = await self.user_repo.retrieve(
            filters=dict(id=user_id),
            related_fields=["agency"]
        )

        if user and user.amocrm_id:
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
