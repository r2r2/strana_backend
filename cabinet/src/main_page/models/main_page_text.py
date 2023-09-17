from src.main_page.entities import BaseMainPageModel


class MainPageTextResponse(BaseMainPageModel):
    """
    Модель ответа контента главной страницы
    """
    text: str
