from typing import List, Type

from src.main_page.entities import BaseMainPageCase
from src.main_page.models import MainPageContentDetailResponse
from src.main_page.repos import (MainPageOfferRepo, MainPagePartnerLogoRepo,
                                 MainPageSellOnlineRepo, MainPageTextRepo)
from src.text_blocks.exceptions import TextBlockNotFoundError

SLUG_OFFER = "offer"
SLUG_PARTNER_LOGO = "partner_logo"
SLUG_SELL_ONLINE = "sell_online"


class MainPageContentListCase(BaseMainPageCase):
    """
    Список контентов главной страницы
    """
    def __init__(
            self,
            main_page_offer_repo: Type[MainPageOfferRepo],
            main_page_partner_logo_repo: Type[MainPagePartnerLogoRepo],
            main_page_sell_online_repo: Type[MainPageSellOnlineRepo],
    ) -> None:
        self.main_page_offer_repo: MainPageOfferRepo = main_page_offer_repo()
        self.main_page_partner_logo_repo: MainPagePartnerLogoRepo = main_page_partner_logo_repo()
        self.main_page_sell_online_repo: MainPageSellOnlineRepo = main_page_sell_online_repo()

    async def __call__(self, slug) -> List[MainPageContentDetailResponse]:
        filters = dict(is_active=True)
        if slug == SLUG_OFFER:
            return await self.main_page_offer_repo.list(filters=filters)
        elif slug == SLUG_PARTNER_LOGO:
            return await self.main_page_partner_logo_repo.list(filters=filters)
        elif slug == SLUG_SELL_ONLINE:
            return await self.main_page_sell_online_repo.list(filters=filters)

        raise TextBlockNotFoundError


class MainPageTextCase(BaseMainPageCase):
    """
    Список контентов главной страницы
    """
    def __init__(
            self,
            main_page_text_repo: Type[MainPageTextRepo],
    ) -> None:
        self.main_page_text_repo: MainPageTextRepo = main_page_text_repo()

    async def __call__(self, slug) -> MainPageContentDetailResponse:
        filters = dict(slug=slug)
        main_page_content = await self.main_page_text_repo.retrieve(filters=filters)

        if not main_page_content:
            raise TextBlockNotFoundError

        return main_page_content
