from typing import Optional

from common.backend.constaints import CitiesTypes
from pydantic import EmailStr
from src.main_page.entities import BaseMainPageModel


class ResponseManagerRetrieveModel(BaseMainPageModel):
    """
    Модель ответа получения менеджера для главной страницы
    """

    name: str
    lastname: str
    patronymic: Optional[str]
    position: Optional[str]
    phone: Optional[str]
    work_schedule: Optional[str]
    photo: dict[str, Optional[str]]
    city: CitiesTypes.serializer
    email: EmailStr

    class Config:
        orm_mode = True
