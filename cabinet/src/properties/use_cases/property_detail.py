from typing import Type

from common.utils import to_global_id
from src.properties.repos import PropertyRepo, Property
from src.properties.services import ImportPropertyService
from ..entities import BasePropertyCase


class PropertyDetailCase(BasePropertyCase):
    """
    Кейс получения количество комнат квартиры по global_id.
    """
    property_type = "GlobalFlatType"

    def __init__(
        self,
        property_repo: Type[PropertyRepo],
        import_property_service: ImportPropertyService,
    ):
        self.property_repo: PropertyRepo = property_repo()
        self.import_property_service: ImportPropertyService = import_property_service

    async def __call__(
        self,
        profitbase_id: str,
    ) -> Property:
        global_id = to_global_id(self.property_type, profitbase_id)

        booking_property: Property = await self.property_repo.retrieve(
            filters=dict(global_id=global_id),
            related_fields=["section", "floor", "property_type"],
        )
        if not booking_property:
            data = dict(global_id=global_id)
            created_booking_property = await self.property_repo.create(data)
            _, booking_property = await self.import_property_service(property=created_booking_property)

        return booking_property
