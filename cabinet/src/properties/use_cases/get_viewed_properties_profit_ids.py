import binascii
from pydantic import ValidationError

from common.utils import from_global_id
from common.backend import repos as backend_repos

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
        backend_properties_repo: type[backend_repos.BackendPropertiesRepo],
    ) -> None:
        self.property_repo: PropertyRepo = property_repo()
        self.backend_properties_repo: backend_repos.BackendPropertiesRepo = backend_properties_repo()

    async def __call__(self, user_id: int) -> list[int]:
        properties_list_ids: list[tuple] = await self.property_repo.list(
            filters=dict(user_favorite_property__client_id=user_id),
            ordering="user_favorite_property__updated_at",
        ).limit(self.limit_favourites_value).values_list("global_id", "profitbase_id")

        correct_properties_list_ids = await self._get_correct_interest_global_ids(properties_list_ids)

        properties_list_ids_data = []
        for properties_list_id in correct_properties_list_ids:
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

    async def _get_correct_interest_global_ids(self, properties_list_ids: list[str]) -> list[str]:
        correct_properties_list_ids = []
        for properties_list_id in properties_list_ids:
            try:
                property_type, backend_property_id = from_global_id(properties_list_id[0])
                property_status_from_portal = await self._get_property_status_from_portal(
                    backend_property_id=int(backend_property_id),
                )
                if property_status_from_portal is not None and property_status_from_portal == PropertyStatuses.FREE:
                    correct_properties_list_ids.append(properties_list_id)
            except (binascii.Error, UnicodeDecodeError, ValidationError, ValueError):
                continue

        return correct_properties_list_ids

    async def _get_property_status_from_portal(self, backend_property_id: int) -> int | None:
        backend_property = await self.backend_properties_repo.retrieve(filters=dict(id=backend_property_id))
        return backend_property.status if backend_property else None
