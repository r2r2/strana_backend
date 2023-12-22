from src.users.repos import UserViewedProperty, UserViewedPropertyRepo
from src.properties.services import ImportPropertyService
from ..entities import BasePropertyCase
from ..repos import Property, PropertyRepo


class AddViewedPropertiesProfitIdCase(BasePropertyCase):
    """
    Добавление объектов недвижимости в просмотренное по profitbase_id.
    """

    def __init__(
        self,
        property_repo: type[PropertyRepo],
        viewed_property_repo: type[UserViewedPropertyRepo],
        import_property_service: ImportPropertyService
    ) -> None:
        self.property_repo: PropertyRepo = property_repo()
        self.viewed_property_repo: UserViewedPropertyRepo = viewed_property_repo()
        self.import_property_service: ImportPropertyService = import_property_service

    async def __call__(self, user_id: int, viewed_profitbase_ids: list[int]) -> list[UserViewedProperty]:
        properties: list[Property] = await self._create_or_update_properties(profitbase_ids=viewed_profitbase_ids)

        viewed_properties: list = []
        for _property in properties:
            viewed_property_filters: dict = dict(client_id=user_id, property_id=_property.id)
            viewed_property: UserViewedProperty = await self.viewed_property_repo.update_or_create(
                filters=viewed_property_filters, data=dict()  # обновлять пока нечего
            )
            viewed_properties.append(viewed_property)
        return viewed_properties

    async def _create_or_update_properties(self, profitbase_ids: list[int]) -> list[Property]:
        """
        Создаём или обновляем объекты недвижимости по данным из БД портала (profitbase_id).
        """

        updated_properties: list = []
        for profitbase_id in profitbase_ids:
            _, updated_property = await self.import_property_service(backend_property_id=profitbase_id)
            if updated_property:
                updated_properties.append(updated_property)
        return updated_properties
