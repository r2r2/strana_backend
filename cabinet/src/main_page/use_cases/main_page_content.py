from typing import List, Type

from src.main_page.entities import BaseMainPageCase
from src.main_page.models import MainPageContentDetailResponse
from src.main_page.repos import MainPageContentRepo


class MainPageContentListCase(BaseMainPageCase):
    """
    Список контентов главной страницы
    """
    def __init__(
            self,
            main_page_content_repo: Type[MainPageContentRepo],
    ) -> None:
        self.main_page_content_repo: MainPageContentRepo = main_page_content_repo()

    async def __call__(self) -> List[MainPageContentDetailResponse]:
        return await self.main_page_content_repo.list()
