from ..entities import BasePropertyCase
from ..repos import Property, PropertyRepo, FeatureRepo


class GetViewedPropertiesCase(BasePropertyCase):
    """
    Получение просмотренных объектов недвижимости
    """
    def __init__(
        self,
        property_repo: type[PropertyRepo],
        feature_repo: type[FeatureRepo],
    ) -> None:
        self.property_repo: PropertyRepo = property_repo()
        self.feature_repo: FeatureRepo = feature_repo()

    async def __call__(self, user_id: int) -> list[Property]:
        feature_qs = self.feature_repo.list()
        properties: list[Property] = await self.property_repo.list(
            filters=dict(user_favorite_property__client_id=user_id),
            prefetch_fields=[
                "project__city",
                "building",
                "floor",
                dict(relation="property_features", queryset=feature_qs, to_attr="features")

            ],
            ordering="user_favorite_property__updated_at",
        ).limit(16)
        return properties
