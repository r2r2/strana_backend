from typing import Optional, Any

from src.menu.entities import BaseMenuModel


class MenuModel(BaseMenuModel):
    id: int
    name: str
    link: str
    icon: Optional[dict[str, Any]]
    hide_desktop: bool


class ResponseMenuListModel(BaseMenuModel):
    """
    Модель ответа списка меню
    """
    result: list[MenuModel]
