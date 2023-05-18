from typing import Any, Type

from ..entities import BaseManagerCase
from ..exceptions import UserNotFoundError
from ..repos import Manager, ManagersRepo


class ManagerRetrieveCase(BaseManagerCase):
    """
    Получение менеджера по его ID
    """

    def __init__(self, manager_repo: Type[ManagersRepo]) -> None:
        self.manager_repo: ManagersRepo = manager_repo()

    async def __call__(self, manager_id: int) -> Manager:
        filters: dict[str, Any] = dict(id=manager_id)
        manager: Manager = await self.manager_repo.retrieve(filters=filters)
        if not manager:
            raise UserNotFoundError
        return manager
