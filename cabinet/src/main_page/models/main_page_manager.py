from typing import Optional

from src.main_page.entities import BaseMainPageModel


class ResponseMainPageManagerRetrieveModel(BaseMainPageModel):
    """
    Модель ответа получения менеджера для главной страницы
    """

    name: str
    lastname: str
    patronymic: Optional[str]
    position: Optional[str]
    phone: Optional[str]
    work_schedule: Optional[str]
    photo: dict[str, Optional[str]] = {}

    class Config:
        orm_mode = True
