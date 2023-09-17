from src.users.repos import UserViewedProperty, UserViewedPropertyRepo
from src.properties.services import ImportPropertyService
from ..entities import BasePropertyCase
from ..repos import Property, PropertyRepo


class AddViewedPropertiesCase(BasePropertyCase):
    """
    Добавление объектов недвижимости в просмотренное
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

    async def __call__(self, user_id: int, viewed_global_ids: list[str]) -> list[UserViewedProperty]:
        properties: list[Property] = await self._create_or_update_properties(global_ids=viewed_global_ids)

        viewed_properties: list = []
        for _property in properties:
            viewed_property_filters: dict = dict(client_id=user_id, property_id=_property.id)
            viewed_property: UserViewedProperty = await self.viewed_property_repo.update_or_create(
                filters=viewed_property_filters, data=dict()  # обновлять пока нечего
            )
            viewed_properties.append(viewed_property)
        return viewed_properties

    async def _create_or_update_properties(self, global_ids: list[str]) -> list[Property]:
        """
        Создаём или обновляем объекты недвижимости по данным из БД портала
        """
        updated_properties: list = []
        for global_id in global_ids:
            data: dict = dict(global_id=global_id)
            _property = await self.property_repo.update_or_create(filters=data, data=dict())
            _, updated_property = await self.import_property_service(property=_property)
            updated_properties.append(updated_property)
        return updated_properties
