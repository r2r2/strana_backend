from typing import Type

from ..entities import BasePropertyCase
from ..repos import PropertyTypeRepo, PropertyType


class PropertyTypeListCase(BasePropertyCase):
    """
    Кейс получения списка типов объектов недвижимости.
    """

    def __init__(
        self,
        property_type_repo: Type[PropertyTypeRepo],
    ) -> None:
        self.property_type_repo: PropertyTypeRepo = property_type_repo()

    async def __call__(self) -> list[PropertyType]:
        property_types: list[PropertyType] = await self.property_type_repo.list(filters=dict(is_active=True))
        return property_types
