from typing import Any, List, Type

from src.main_page.entities import BaseMainPageCase
from src.main_page.models import MainPagePartnerLogoDetailResponse
from src.main_page.repos import MainPagePartnerLogoRepo


class MainPagePartnerLogoListCase(BaseMainPageCase):
    """
    Список блока "Логотипы партнёров" главной страницы
    """
    def __init__(
            self,
            main_page_partner_logo_repo: Type[MainPagePartnerLogoRepo],
    ) -> None:
        self.main_page_partner_logo_repo: MainPagePartnerLogoRepo = main_page_partner_logo_repo()

    async def __call__(self) -> List[MainPagePartnerLogoDetailResponse]:
        filters: dict[str, Any] = dict(is_active=True)
        return await self.main_page_partner_logo_repo.list(filters=filters)
