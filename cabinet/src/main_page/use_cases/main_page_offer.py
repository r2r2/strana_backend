from typing import Any, List, Type

from src.main_page.entities import BaseMainPageCase
from src.main_page.models import MainPageOfferDetailResponse
from src.main_page.repos import MainPageOfferRepo


class MainPageOfferListCase(BaseMainPageCase):
    """
    Список блока "Что мы предлагаем" главной страницы
    """
    def __init__(
            self,
            main_page_offer_repo: Type[MainPageOfferRepo],
    ) -> None:
        self.main_page_offer_repo: MainPageOfferRepo = main_page_offer_repo()

    async def __call__(self) -> List[MainPageOfferDetailResponse]:
        filters: dict[str, Any] = dict(is_active=True)
        return await self.main_page_offer_repo.list(filters=filters)
