from copy import copy
from typing import Optional, Type

import tortoise
from common.backend.models import BackendCity
from common.backend.repos import BackendCitiesRepo

from ..entities import BaseCityService
from ..repos import CityRepo


class ImportCitiesService(BaseCityService):
    """
    Импорт городов из БД
    """

    def __init__(
        self,
        orm_class: Optional[Type[tortoise.Tortoise]],
        orm_config: Optional[dict],
        backend_city_repo: Type[BackendCitiesRepo],
        city_repo: Type[CityRepo],
    ):
        self.backend_city_repo = backend_city_repo()
        self.city_repo = city_repo()
        self.orm_class = orm_class
        self.orm_config = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

    async def __call__(self):
        filters = dict(active=True)
        backend_cities: list[BackendCity] = await self.backend_city_repo.list(filters=filters)
        for backend_city in backend_cities:
            filters = dict(id=backend_city.id)
            city_data = dict(name=backend_city.name, slug=backend_city.slug)
            await self.city_repo.update_or_create(filters=filters, data=city_data)
