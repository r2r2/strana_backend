from src.main_page.entities import BaseMainPageModel


class MainPageContentDetailResponse(BaseMainPageModel):
    """
    Модель ответа контента главной страницы
    """
    text: str
    slug: str
