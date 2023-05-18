from typing import Any, Type

from ..repos import User, AdminRepo
from ..entities import BaseAdminCase
from ..exceptions import AdminNotFoundError


class GetMeCase(BaseAdminCase):
    """
    Получение текущего администратора
    """

    def __init__(self, admin_repo: Type[AdminRepo]) -> None:
        self.admin_repo: AdminRepo = admin_repo()

    async def __call__(self, admin_id: int) -> User:
        filters: dict[str, Any] = dict(id=admin_id)
        admin: User = await self.admin_repo.retrieve(filters=filters)
        if not admin:
            raise AdminNotFoundError
        return admin
