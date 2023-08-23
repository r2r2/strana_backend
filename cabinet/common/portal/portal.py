import json
from typing import Type, Any

from pydantic import parse_obj_as

from common.requests import GraphQLRequest
from config import backend_config
from src.cities.models import CityPortalModel


class PortalAPI:
    ALL_CITIES = "allCities"
    ALL_NEWS = "allNews"

    query_directory: str = "/common/portal/queries/"

    def __init__(
            self,
            request_class: Type[GraphQLRequest],
            portal_config: backend_config
    ):
        self._request_class = request_class
        self.portal_host: str = portal_config["url"]
        self.portal_graphql: str = portal_config["graphql"]

    async def get_all_news(self, city_global_id) -> list:
        request_data: dict[str, Any] = dict(url=self.portal_host + self.portal_graphql,
                                            type=self.ALL_NEWS,
                                            query_name=self.ALL_NEWS + ".graphql",
                                            query_directory=self.query_directory,
                                            filters=(json.dumps(city_global_id))
                                            )
        async with self._request_class(**request_data) as response:
            response_data = [i["node"] for i in response.data["edges"]]

        return response_data

    async def get_all_cities(self) -> list[CityPortalModel]:
        request_data: dict[str, Any] = dict(url=self.portal_host + self.portal_graphql,
                                            type=self.ALL_CITIES,
                                            query_name=self.ALL_CITIES + ".graphql",
                                            query_directory=self.query_directory,
                                            filters=("name",))
        async with self._request_class(**request_data) as response:
            response_data = [i["node"] for i in response.data["edges"]]

        return parse_obj_as(list[CityPortalModel], response_data)
