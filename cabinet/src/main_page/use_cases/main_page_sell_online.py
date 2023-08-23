from typing import Any, List, Type

from src.main_page.entities import BaseMainPageCase
from src.main_page.models import MainPageSellOnlineDetailResponse
from src.main_page.repos import MainPageSellOnlineRepo


class MainPageSellOnlineListCase(BaseMainPageCase):
    """
    Список блока "Продавайте онлайн" главной страницы
    """
    def __init__(
            self,
            main_page_sell_online_repo: Type[MainPageSellOnlineRepo],
    ) -> None:
        self.main_page_sell_online_repo: MainPageSellOnlineRepo = main_page_sell_online_repo()

    async def __call__(self) -> List[MainPageSellOnlineDetailResponse]:
        filters: dict[str, Any] = dict(is_active=True)
        return await self.main_page_sell_online_repo.list(filters=filters)
