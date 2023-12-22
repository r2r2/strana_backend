import binascii

from common.utils import from_global_id
from pydantic import ValidationError

from ..entities import BasePropertyCase
from ..repos import PropertyRepo
from ..constants import PropertyStatuses


class GetViewedPropertiesProfitIdsCase(BasePropertyCase):
    """
    Получение списка profitbase_id просмотренных объектов недвижимости.
    """
    limit_favourites_value = 16

    def __init__(
        self,
        property_repo: type[PropertyRepo],
    ) -> None:
        self.property_repo: PropertyRepo = property_repo()

    async def __call__(self, user_id: int) -> list[int]:
        properties_list_ids: list[tuple] = await self.property_repo.list(
            filters=dict(
                user_favorite_property__client_id=user_id,
                status=PropertyStatuses.FREE,
            ),
            ordering="user_favorite_property__updated_at",
        ).limit(self.limit_favourites_value).values_list("global_id", "profitbase_id")

        properties_list_ids_data = []
        for properties_list_id in properties_list_ids:
            if properties_list_id[1]:
                properties_list_ids_data.append(properties_list_id[1])
            else:
                if profitbase_id := self._get_profitbase_id(global_id=properties_list_id[0]):
                    properties_list_ids_data.append(profitbase_id)

        return properties_list_ids_data

    def _get_profitbase_id(self, global_id: str) -> int | None:
        try:
            profitbase_id = int(from_global_id(global_id)[1])
        except (binascii.Error, UnicodeDecodeError, ValidationError, ValueError):
            profitbase_id = None
        return profitbase_id
