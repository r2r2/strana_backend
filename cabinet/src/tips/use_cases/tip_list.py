from typing import Type, Any

from ..entities import BaseTipCase
from ..repos import TipRepo, Tip


class TipListCase(BaseTipCase):
    """
    Список подсказок
    """

    def __init__(self, tip_repo: Type[TipRepo]) -> None:
        self.tip_repo: TipRepo = tip_repo()

    async def __call__(self) -> dict[str, Any]:
        tips: list[Tip] = await self.tip_repo.list()
        data: dict[str, Any] = dict(result=tips, count=len(tips))
        return data

