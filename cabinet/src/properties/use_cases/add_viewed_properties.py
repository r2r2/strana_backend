from src.users.repos import UserViewedProperty, UserViewedPropertyRepo
from ..entities import BasePropertyCase
from ..exceptions import PropertiesNotFoundError
from ..repos import Property, PropertyRepo


class AddViewedPropertiesCase(BasePropertyCase):
    """
    Добавление объектов недвижимости в просмотренное
    """
    def __init__(
        self,
        property_repo: type[PropertyRepo],
        viewed_property_repo: type[UserViewedPropertyRepo],
    ) -> None:
        self.property_repo: PropertyRepo = property_repo()
        self.viewed_property_repo: UserViewedPropertyRepo = viewed_property_repo()

    async def __call__(self, user_id: int, viewed_global_ids: list[str]) -> list[UserViewedProperty]:
        property_filters: dict = dict(global_id__in=viewed_global_ids)
        properties: list[Property] = await self.property_repo.list(filters=property_filters)

        if not properties:
            raise PropertiesNotFoundError

        viewed_properties: list = []
        for _property in properties:
            viewed_property_filters: dict = dict(client_id=user_id, property_id=_property.id)
            viewed_property: UserViewedProperty = await self.viewed_property_repo.update_or_create(
                filters=viewed_property_filters, data=dict() # обновлять пока нечего
            )
            viewed_properties.append(viewed_property)
        return viewed_properties
