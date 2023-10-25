from typing import Type

from common.utils import to_global_id
from src.properties.repos import PropertyRepo, Property
from ..entities import BasePropertyCase
from ..exceptions import PropertyNotFoundError


class PropertyDetailCase(BasePropertyCase):
    """
    Кейс получения количество комнат квартиры по global_id.
    """
    property_type = "GlobalFlatType"

    def __init__(self, property_repo: Type[PropertyRepo]):
        self.property_repo: PropertyRepo = property_repo()

    async def __call__(
        self,
        profitbase_id: str,
    ) -> Property:
        global_id = to_global_id(self.property_type, profitbase_id)

        property_info: Property = await self.property_repo.retrieve(
            filters=dict(global_id=global_id),
            related_fields=["section", "floor", "property_type"],
        )
        if not property_info:
            raise PropertyNotFoundError

        return property_info
