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

    async def __call__(self) -> Manager:
        main_page_managers: Manager = await self.main_page_manager_repo.list(related_fields=["manager"], end=1)
        if not main_page_managers:
            raise ManagerNotFoundError

        main_page_manager = main_page_managers[0].manager
        main_page_manager.position = main_page_managers[0].position
        main_page_manager.photo = main_page_managers[0].photo

        return main_page_manager
