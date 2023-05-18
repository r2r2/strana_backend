import datetime
from typing import Any, Type
import zlib


from ..entities import BaseUserCase
from ..exceptions import UserNotFoundError
from ..repos import UserRepo, User


class SuperuserUserFillDataCase(BaseUserCase):
    """
    Обновление данных пользователей в АмоСРМ после изменения в админке брокера.
    """

    def __init__(
        self,
        user_repo: Type[UserRepo],
        update_user_service: Any,
    ) -> None:
        self.user_repo: UserRepo = user_repo()
        self.update_user_service: Any = update_user_service

    async def __call__(
        self,
        user_id: int,
        data: int,
    ) -> User:
        user: User = await self.user_repo.retrieve(
            filters=dict(id=user_id),
            related_fields=["agency"]
        )
        if not user:
            raise UserNotFoundError

        hash_date = zlib.crc32(bytes(str(datetime.datetime.now().date()), 'utf-8'))

        if user.amocrm_id and data == hash_date:

            await self.update_user_service(user=user)

        return user
