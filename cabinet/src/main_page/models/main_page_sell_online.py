from src.main_page.entities import BaseMainPageModel


class MainPageSellOnlineDetailResponse(BaseMainPageModel):
    """
    Модель ответа "Продавайте онлайн" на главной странице
    """
    title: str
    description: str

    class Config:
        orm_mode = True
