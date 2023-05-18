from typing import Type, Any

from ..entities import BasePageCase
from ..repos import CheckUniqueRepo, CheckUnique


class CheckUniqueRetrieveCase(BasePageCase):
    """
    Страница проверки на уникальность
    """

    def __init__(self, check_unique_repo: Type[CheckUniqueRepo]) -> None:
        self.check_unique_repo: CheckUniqueRepo = check_unique_repo()

    async def __call__(self) -> CheckUnique:
        filters: dict[str, Any] = dict()
        check_unique: CheckUnique = await self.check_unique_repo.retrieve(filters=filters)
        return check_unique
