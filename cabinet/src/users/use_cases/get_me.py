from typing import Any, Type

from ..repos import User, UserRepo
from ..entities import BaseUserCase
from ..exceptions import UserNotFoundError


class GetMeCase(BaseUserCase):
    """
    Получение текущего пользователя
    """

    def __init__(self, user_repo: Type[UserRepo]) -> None:
        self.user_repo: UserRepo = user_repo()

    async def __call__(self, user_id: int) -> User:
        filters: dict[str, Any] = dict(id=user_id)
        user: User = await self.user_repo.retrieve(filters=filters)
        if not user:
            raise UserNotFoundError
        return user
