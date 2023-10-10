from typing import Any, Type

from ..repos import User, RepresRepo
from ..entities import BaseRepresCase
from ..exceptions import RepresNotFoundError


class GetMeCase(BaseRepresCase):
    """
    Получение текущего представителя
    """

    def __init__(self, repres_repo: Type[RepresRepo]) -> None:
        self.repres_repo: RepresRepo = repres_repo()

    async def __call__(self, repres_id: int) -> User:
        filters: dict[str, Any] = dict(id=repres_id)
        repres: User = await self.repres_repo.retrieve(filters=filters, related_fields=["agency", "agency__general_type"])
        if not repres:
            raise RepresNotFoundError
        return repres
