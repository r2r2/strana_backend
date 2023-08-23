from typing import Any, Optional

from src.main_page.entities import BaseMainPageModel


class MainPagePartnerLogoDetailResponse(BaseMainPageModel):
    """
    Модель ответа логотипов партнёров на главной странице
    """
    image: Optional[dict[str, Any]]

    class Config:
        orm_mode = True
