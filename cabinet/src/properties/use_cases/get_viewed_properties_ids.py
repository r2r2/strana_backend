from ..entities import BasePropertyCase
from ..repos import PropertyRepo


class GetViewedPropertiesIdsCase(BasePropertyCase):
    """
    Получение списка global_id просмотренных объектов недвижимости
    """
    def __init__(
        self,
        property_repo: type[PropertyRepo],
    ) -> None:
        self.property_repo: PropertyRepo = property_repo()

    async def __call__(self, user_id: int) -> list[str]:
        properties_list_ids: list[str] = await self.property_repo.list(
            filters=dict(user_favorite_property__client_id=user_id),
            ordering="user_favorite_property__updated_at",
        ).limit(16).values_list("global_id", flat=True)
        return properties_list_ids
