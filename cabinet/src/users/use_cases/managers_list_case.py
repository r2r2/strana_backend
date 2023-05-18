from typing import Any, Type

from ..entities import BaseUserCase
from ..exceptions import UserNotFoundError
from ..repos import Manager, ManagersRepo


class ManagersListCase(BaseUserCase):
    """
    Кейс списка менеджеров
    """

    def __init__(
            self,
            manager_repo: Type[ManagersRepo],

    ) -> None:
        self.manager_repo: ManagersRepo = manager_repo()

    async def __call__(self, init_filters: dict[str, Any]) -> dict[str, Any]:
        filters: dict[str, Any] = init_filters
        managers: list[Manager] = await self.manager_repo.list(filters=filters)
        if not managers:
            raise UserNotFoundError
        data: dict[str, Any] = dict(result=managers)
        return data
