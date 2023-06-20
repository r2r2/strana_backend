from typing import Type

from ..repos import City, CityRepo
from ..entities import BaseCityCase
from ..exceptions import CitiesNotFoundError


class CitiesListCase(BaseCityCase):
    """
    Кейс для списка городов
    """
    def __init__(self, city_repo: Type[CityRepo]) -> None:
        self.city_repo: CityRepo = city_repo()

    async def __call__(self) -> list[City]:
        cities_filter: dict = dict(
            slug__not="",
            name__not="Не определен",
            projects__isnull=False,
        )

        cities: list[City] = await self.city_repo.list(
            filters=cities_filter,
        ).distinct()
        if not cities:
            raise CitiesNotFoundError

        return cities
