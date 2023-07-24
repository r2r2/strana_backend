from copy import copy
from typing import Optional, Type

import tortoise

from common.portal.portal import PortalAPI
from src.cities.models.city import CityPortalModel
from src.cities.repos import CityRepo


class UpdateCitiesService:
    """
    Обновление списка городов
    """
    def __init__(
            self,
            cities_repo: Type[CityRepo],
            portal_class: PortalAPI,
            orm_class: Optional[Type[tortoise.Tortoise]],
            orm_config: Optional[dict],
    ):
        self.orm_class = orm_class
        self.orm_config = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)
        self.cities_repo = cities_repo()
        self.portal_class = portal_class

    async def __call__(self):
        cities: list[CityPortalModel] = await self.portal_class.get_all_cities()

        for city in cities:
            city_dict = city.dict()
            if not city_dict.get("slug"):
                continue
            filters: dict = dict(slug=city_dict.pop("slug"))
            city_dict["global_id"] = city_dict.pop("id")
            await self.cities_repo.update_or_create(filters=filters, data=city_dict)
