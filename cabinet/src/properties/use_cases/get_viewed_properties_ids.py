import binascii
from pydantic import ValidationError

from common.utils import from_global_id
from common.backend import repos as backend_repos

from src.users.repos import UserViewedPropertyRepo
from ..constants import PropertyStatuses
from ..entities import BasePropertyCase
from ..repos import PropertyRepo


class GetViewedPropertiesIdsCase(BasePropertyCase):
    """
    Получение списка global_id просмотренных объектов недвижимости
    """
    def __init__(
        self,
        property_repo: type[PropertyRepo],
        viewed_property_repo: type[UserViewedPropertyRepo],
        backend_properties_repo: type[backend_repos.BackendPropertiesRepo],
    ) -> None:
        self.property_repo: PropertyRepo = property_repo()
        self.viewed_property_repo: UserViewedPropertyRepo = viewed_property_repo()
        self.backend_properties_repo: backend_repos.BackendPropertiesRepo = backend_properties_repo()

    async def __call__(self, user_id: int) -> list[str]:
        properties_list_ids: list[str] = await self.viewed_property_repo.list(
            filters=dict(client_id=user_id),
            related_fields=["property"],
            ordering="-updated_at",
        ).limit(24).values_list("property__global_id", flat=True)

        correct_properties_list_ids = await self._get_correct_interest_global_ids(properties_list_ids)
        return correct_properties_list_ids[:16]

    async def _get_correct_interest_global_ids(self, properties_list_ids: list[str]) -> list[str]:
        correct_properties_list_ids = []
        for properties_list_id in properties_list_ids:
            try:
                property_type, backend_property_id = from_global_id(properties_list_id)
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
