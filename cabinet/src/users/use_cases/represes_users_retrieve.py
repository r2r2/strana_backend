from typing import Any, Type

from ..constants import UserType
from ..entities import BaseUserCase
from ..exceptions import UserNotFoundError
from ..repos import CheckRepo, User, UserRepo, UserPinningStatusRepo


class RepresesUsersRetrieveCase(BaseUserCase):
    """
    Пользователь представителя агенства
    """

    def __init__(
        self,
        user_repo: Type[UserRepo],
        check_repo: Type[CheckRepo],
        user_pinning_repo: Type[UserPinningStatusRepo],
    ) -> None:
        self.user_repo: UserRepo = user_repo()
        self.check_repo: CheckRepo = check_repo()
        self.user_pinning_repo = user_pinning_repo()

    async def __call__(self, user_id: int, agency_id: int) -> User:
        filters: dict[str, Any] = dict(id=user_id, agency_id=agency_id, type=UserType.CLIENT)
        user: User = await self.user_repo.retrieve(
            filters=filters,
            related_fields=["agent", "agency"],
            prefetch_fields=[
                dict(relation="users_checks",
                     queryset=self.check_repo.list(ordering="-requested"),
                     to_attr="statuses"),
                dict(relation="users_pinning_status",
                     queryset=self.user_pinning_repo.list(),
                     to_attr="pinning_statuses"),
            ],
        )
        if not user:
            raise UserNotFoundError
        user.status = next(iter(user.statuses), None)
        user.pinning_status = next(iter(user.pinning_statuses), None)
        return user
