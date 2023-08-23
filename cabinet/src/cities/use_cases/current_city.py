from typing import Type, Any

from common.requests import CommonRequest
from config import dadata_config
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
            iplocation_repo: Type[city_repo.IPLocationRepo],
            cities_repo: Type[city_repo.CityRepo],
            request_class: Type[CommonRequest],
    ):
        self.iplocation_repo = iplocation_repo()
        self.cities_repo = cities_repo()
        self._request_class: Type[CommonRequest] = request_class
        self._dadata_url = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/iplocate/address"

    async def __call__(self, ip_address: str):
        if location := await self.iplocation_repo.retrieve(filters=dict(ip_address=ip_address),
                                                           related_fields=["city"]):
            return location.city
        headers: dict[str, Any] = {
            "Content-type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Token {dadata_config['token']}",
            "X-Secret": dadata_config['secret'],
        }
        request_data: dict[str, Any] = dict(
            url=self._dadata_url,
            method="GET",
            headers=headers,
            query={"ip": ip_address},
        )
        try:
            async with self._request_class(**request_data) as response:
                dadata_city = response.data["location"]["data"]["city"]
            city = await self.cities_repo.retrieve(dict(name=dadata_city))
        except:
            return await self.cities_repo.retrieve(dict(name="Тюмень"))
        if city:
            await self.iplocation_repo.create(dict(ip_address=ip_address, city=city))
            return city
        else:
            return await self.cities_repo.retrieve(dict(name="Тюмень"))
