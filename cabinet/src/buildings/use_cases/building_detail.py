from typing import Type

from ..entities import BaseBuildingCase
from ..repos import BuildingRepo


class BuildingDetailCase(BaseBuildingCase):
    """
    Получение корпуса
    """
    def __init__(self, building_repo: Type[BuildingRepo]) -> None:
        self.building_repo: BuildingRepo = building_repo()

    async def __call__(self, building_id: int):
        return await self.building_repo.retrieve(filters=dict(id=building_id), prefetch_fields=["project__city"])
