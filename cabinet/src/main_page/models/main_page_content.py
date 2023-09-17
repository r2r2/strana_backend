from typing import Any, Optional

from src.main_page.entities import BaseMainPageModel


class MainPageContentDetailResponse(BaseMainPageModel):
    """
    Модель ответа контента для главной страницы
    """
    title: Optional[str]
    description: Optional[str]
    image: Optional[dict[str, Any]]
