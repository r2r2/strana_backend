from string import Template
from typing import Type, Any, Optional

from pydantic import parse_obj_as

from common.cache.decorators import cache_storage
from common.calculator.calculator import CalculatorAPI
from common.portal.portal import PortalAPI
from common.requests import CommonResponse
from config import backend_config
from src.booking import repos as booking_repos
from src.cities import repos as cities_repos
from src.dashboard import repos as dashboard_repos
from src.dashboard.entities import BaseDashboardCase
from src.dashboard.models.block import BlockListResponse, ElementRetrieveModel
from src.users import repos as user_repos


class GetDashboardListCase(BaseDashboardCase):
    SUCCESS_BOOKING_STATUS_ID = 142
    PORTAL_ENDPOINT = "/promo/"

    def __init__(
        self,
        dashboard_block: Type[dashboard_repos.BlockRepo],
        elements_repo: Type[dashboard_repos.ElementRepo],
        city_repo: Type[cities_repos.CityRepo],
        user_repo: Type[user_repos.UserRepo],
        booking_repo: Type[booking_repos.BookingRepo],
        link_repo: Type[dashboard_repos.LinkRepo],
        portal_class: PortalAPI,
        calculator_class: CalculatorAPI,
        mc_config: dict[str, Any],
        portal_config: backend_config
    ):
        self.block_repo = dashboard_block()
        self.elements_repo = elements_repo()
        self.city_repo = city_repo()
        self.user_repo = user_repo()
        self.booking_repo = booking_repo()
        self.link_repo = link_repo()
        self.portal_class: PortalAPI = portal_class
        self.calculator_class: CalculatorAPI = calculator_class
        self.mc_config = mc_config
        self.portal_external_host = portal_config["external_url"]

    async def __call__(self, city_slug: str, user_id: Optional[int] = None) -> list[BlockListResponse]:
        slug_filter = dict(city__slug=city_slug)
        link_qs = self.link_repo.list(filters=slug_filter)
        element_qs = self.elements_repo.list(
            filters=slug_filter,
            ordering="priority",
            prefetch_fields=[
                dict(relation="links", queryset=link_qs, to_attr="link_list"),
            ]
        )
        blocks: list[dashboard_repos.Block] = await self.block_repo.list(
            filters=slug_filter, prefetch_fields=[dict(relation="elements", queryset=element_qs,
                                                       to_attr="elements_list")])
        blocks_resp = []

        template_dict = dict(
            calculator_baner=await self.get_mortgage_calc_data(city_slug),
        )
        portal_news = await self.get_portal_news(city_slug)

        if not user_id:
            user_has_success_booking = False
        else:
            bookings_qs = self.booking_repo.list(filters=dict(amocrm_status__id=self.SUCCESS_BOOKING_STATUS_ID))
            user = await self.user_repo.retrieve(filters=dict(id=user_id),
                                                 prefetch_fields=[dict(relation="bookings", queryset=bookings_qs,
                                                                       to_attr="bookings_list")])
            if user.bookings_list:
                user_has_success_booking = True
            else:
                user_has_success_booking = False

        for block in blocks:
            if block.elements:
                elements_list = []
                proxy_block = self.build_block(block, template_dict)
                for element in block.elements:
                    if element.has_completed_booking and not user_has_success_booking:
                        continue
                    elif element.type == "stock_slider" and portal_news:
                        for node in portal_news:
                            template_dict["portal_news"] = node["title"]
                            proxy_element = self.build_element(element, template_dict)
                            proxy_element.id = node["id"]
                            proxy_element.expires = node["end"]
                            proxy_element.link = self.portal_external_host + f"/{city_slug}" + \
                                                 self.PORTAL_ENDPOINT + node["slug"]
                            proxy_element.image = dict(aws=node["cardImageDisplay"])
                            elements_list.append(proxy_element)
                            template_dict.pop("portal_news")
                    else:
                        proxy_element = self.build_element(element, template_dict)
                        elements_list.append(proxy_element)

                if elements_list:
                    proxy_block.elements_list = elements_list
                    blocks_resp.append(proxy_block)
        return blocks_resp

    @staticmethod
    def build_block(block: dashboard_repos.Block, template_dict: dict[str, str]):
        proxy_block = parse_obj_as(BlockListResponse, block)
        proxy_block.title = Template(proxy_block.title).safe_substitute(template_dict)
        proxy_block.description = Template(proxy_block.description).safe_substitute(template_dict)
        return proxy_block

    @staticmethod
    def build_element(element: dashboard_repos.Element, template_dict: dict[str, str]):
        proxy_element = parse_obj_as(ElementRetrieveModel, element)
        proxy_element.title = Template(proxy_element.title).safe_substitute(template_dict)
        proxy_element.description = Template(proxy_element.description).safe_substitute(template_dict)
        if element.links:
            proxy_element.link = element.links[0].link
        return proxy_element

    @cache_storage
    async def get_mortgage_calc_data(self, city_slug: str) -> str:
        response: CommonResponse = await self.calculator_class.get_mortgage_calc_data(city_slug)
        return response.data['bannerMinRate']
        # return "5.31"

    @cache_storage
    async def get_portal_news(self, city_slug: str) -> list:
        city = await self.city_repo.retrieve(filters=dict(slug=city_slug))
        news = await self.portal_class.get_all_news(city.global_id)
        return news
        # return [
        #     {"id": "TmV3c1R5cGU6MTQ0NA==", "title": "У нас есть акция 1", "end": "2023-11-30T16:00:00+00:00",},
        #     {"id": "TmV3c1R5cGU6MTYxOQ==", "title": "У нас есть акция 2", "end": "2023-11-30T16:00:00+00:00",},
        # ]
