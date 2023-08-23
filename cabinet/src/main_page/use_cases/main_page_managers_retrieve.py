from typing import Any, Type

from src.main_page.entities import BaseMainPageCase
from src.main_page.exceptions import ManagerNotFoundError
from src.main_page.repos import MainPageManagerRepo
from src.users.repos import Manager


class MainPageManagerRetrieveCase(BaseMainPageCase):
    """
    Получение менеджера главной страницы
    """
    def __init__(self, main_page_manager_repo: Type[MainPageManagerRepo]) -> None:
        self.main_page_manager_repo: MainPageManagerRepo = main_page_manager_repo()

    async def __call__(self, manager_id: int) -> Manager:
        filters: dict[str, Any] = dict(id=manager_id)
        main_page_manager: Manager = await self.main_page_manager_repo.retrieve(
            filters=filters,
            related_fields=["manager"],
        )
        if not main_page_manager:
            raise ManagerNotFoundError

        return main_page_manager.manager
