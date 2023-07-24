from typing import Type, Any, Coroutine, Callable

from pydantic import parse_obj_as

from common.portal.portal import PortalAPI
from common.requests import CommonRequest, CommonResponse
from src.cities import repos as cities_repos
from src.dashboard import repos as dashboard_repos
from src.dashboard.entities import BaseDashboardCase
from src.dashboard.models.block import BlockListResponse, _ElementRetrieveModel


class GetDashboardListCase(BaseDashboardCase):

    def __init__(
            self,
            dashboard_block: Type[dashboard_repos.BlockRepo],
            elements_repo: Type[dashboard_repos.ElementRepo],
            city_repo: Type[cities_repos.CityRepo],
            link_repo: Type[dashboard_repos.LinkRepo],
            portal_class: PortalAPI,
            request_class: Type[CommonRequest],
            mc_config: dict[str, Any]
    ):
        self.block_repo = dashboard_block()
        self.elements_repo = elements_repo()
        self.city_repo = city_repo()
        self.link_repo = link_repo()
        self.portal_class: PortalAPI = portal_class
        self.request_class: Type[CommonRequest] = request_class
        self.mc_config = mc_config

        self.slug_to_def_mapper = {
            "mc_banner": self.get_mortgage_calc_data,
            "portal_news": self.get_portal_news
        }

    async def __call__(self, city_slug: str) -> list[BlockListResponse]:
        link_qs = self.link_repo.list()
        slug_filter = dict(city__slug=city_slug)
        element_qs = self.elements_repo.list(filters=slug_filter,
                                             prefetch_fields=[dict(relation="links", queryset=link_qs,
                                                                    to_attr="link_list")])
        blocks: list[dashboard_repos.Block] = await self.block_repo.list(
            filters=slug_filter, prefetch_fields=[dict(relation="elements", queryset=element_qs,
                                                       to_attr="elements_list")])
        blocks_resp = []
        for block in blocks:
            if block.elements:
                elements_list = []
                proxy_block = parse_obj_as(BlockListResponse, block)
                for element in block.elements:
                    proxy_element = parse_obj_as(_ElementRetrieveModel, element)
                    if element.slug in self.slug_to_def_mapper.keys():
                        description = await self.slug_to_def_mapper[element.slug](city_slug, element.description)
                        proxy_element.description = description
                    if element.links:
                        proxy_element.link = [link.link for link in element.links]
                    elements_list.append(proxy_element)

                proxy_block.elements_list = elements_list
                blocks_resp.append(proxy_block)
        return blocks_resp

    async def get_mortgage_calc_data(self, city_slug: str, e_description: str) -> str:
        request_data: dict[str, Any] = dict(
            url=self.mc_config["url"] + "/v1/banners",
            method="GET",
            query=dict(city=city_slug)
        )
        request_get: Callable[..., Coroutine] = self.request_class(**request_data)
        response: CommonResponse = await request_get()
        return e_description.format(response.data['bannerMinRate'])

    async def get_portal_news(self, city_slug: str, e_description: str):
        city = await self.city_repo.retrieve(filters=dict(slug=city_slug))
        news = await self.portal_class.get_all_news(city.global_id)
        return e_description.format(news[0]["shortDescription"])
