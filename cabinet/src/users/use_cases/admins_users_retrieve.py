from typing import Any, Type

from ..constants import UserType
from ..entities import BaseUserCase
from ..exceptions import UserNotFoundError
from ..repos import CheckRepo, User, UserRepo


class AdminsUsersRetrieveCase(BaseUserCase):
    """
    Пользователь администратором
    """

    def __init__(
        self,
        user_repo: Type[UserRepo],
        check_repo: Type[CheckRepo],
    ) -> None:
        self.user_repo: UserRepo = user_repo()
        self.check_repo: CheckRepo = check_repo()

    async def __call__(self, user_id: int) -> User:
        filters: dict[str, Any] = dict(id=user_id, type=UserType.CLIENT)
        user: User = await self.user_repo.retrieve(
            filters=filters,
            related_fields=["agent", "agency"],
            prefetch_fields=[
                dict(relation="users_checks",
                     queryset=self.check_repo.list(ordering="-requested"),
                     to_attr="statuses")
            ],
        )
        if not user:
            raise UserNotFoundError
        user.status = next(iter(user.statuses), None)
        return user