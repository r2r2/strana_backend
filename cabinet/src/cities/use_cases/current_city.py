from decimal import Decimal

from dadata import DadataAsync
from haversine import haversine
from httpx import HTTPError

from src.cities import repos as city_repo
from ..entities import BaseCityCase


class CurrentCity(BaseCityCase):
    """
    Класс который определяет место положение по айпи
    (прям как в детстве на серваках cs 1.6 обещали вычислить по айпи, гештальт закрыт)
    Если как-то менять логику связи айпи и города то желательно почистить cities_iplocation табличку
    """

    def __init__(
            self,
            iplocation_repo: type[city_repo.IPLocationRepo],
            dadata_settings_repo: type[city_repo.DaDataSettingsRepo],
            cities_repo: type[city_repo.CityRepo],
    ):
        self.iplocation_repo = iplocation_repo()
        self.dadata_settings_repo = dadata_settings_repo()
        self.cities_repo = cities_repo()

    async def __call__(self, ip_address: str):
        if location := await self.iplocation_repo.retrieve(filters=dict(ip_address=ip_address),
                                                           related_fields=["city"]):
            return location.city

        dadata_settings = await self.dadata_settings_repo.list().first()

        try:
            async with DadataAsync(dadata_settings.api_key, dadata_settings.secret_key) as dadata:
                result = await dadata.iplocate(ip_address)
        except HTTPError as e:
            self.logger.info("Не удалось получить данные из DaData.", e)
            return await self.cities_repo.retrieve(dict(name="Тюмень"))
        except Exception as e:
            self.logger.exception("Произошла неизвестная ошибка")
            return await self.cities_repo.retrieve(dict(name="Тюмень"))
        if not result or 'data' not in result.keys():
            return await self.cities_repo.retrieve(dict(name="Тюмень"))

        current_geo = (Decimal(result['data']['geo_lat']), Decimal(result['data']['geo_lon']))

        filters = dict(
            latitude__isnull=False,
            longitude__isnull=False,
        )
        cites = await self.cities_repo.list(filters=filters)

        city_coordinates = {city: (city.latitude, city.longitude) for city in cites}

        distances = float('inf')
        city = None
        for city_key, city_coord in city_coordinates.items():
            if distances > haversine(city_coord, current_geo):
                city = city_key
                distances = haversine(city_coord, current_geo)

        if city:
            await self.iplocation_repo.create(dict(ip_address=ip_address, city=city))
            return city

        return await self.cities_repo.retrieve(dict(name="Тюмень"))
