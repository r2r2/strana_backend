from typing import Optional

from pydantic import EmailStr

from ..entities import BaseManagerModel
from common.backend.constaints import CitiesTypes


class RequestGetMeModel(BaseManagerModel):
    """
    Модель запроса получения текущего пользователя
    """

    class Config:
        orm_mode = True


class ResponseManagerRetrieveModel(BaseManagerModel):
    """
    Модель ответа получения текущего пользователя
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


class ResponseManagersListModel(BaseManagerModel):
    result: list[ResponseManagerRetrieveModel]
