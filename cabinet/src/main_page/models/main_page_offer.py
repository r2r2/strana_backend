from typing import Any, Optional

from src.main_page.entities import BaseMainPageModel


class MainPageOfferDetailResponse(BaseMainPageModel):
    """
    Модель ответа предложений на главной странице
    """
    title: str
    description: str
    image: Optional[dict[str, Any]]

    class Config:
        orm_mode = True
