from ..entities import BasePropertyCase
from ..repos import Property, PropertyRepo


class GetViewedPropertiesCase(BasePropertyCase):
    """
    Получение просмотренных объектов недвижимости
    """
    def __init__(
        self,
        property_repo: type[PropertyRepo],
    ) -> None:
        self.property_repo: PropertyRepo = property_repo()

    async def __call__(self, user_id: int) -> list[Property]:
        properties: list[Property] = await self.property_repo.list(
            filters=dict(user_favorite_property__client_id=user_id),
            ordering="user_favorite_property__updated_at",
        ).limit(16)
        return properties
