from datetime import date
from typing import Optional
from ..entities import BaseUserModel
from ..constants import UserType


class RequestGetMeModel(BaseUserModel):
    """
    Модель запроса получения текущего пользователя
    """

    class Config:
        orm_mode = True


class ResponseGetMeModel(BaseUserModel):
    """
    Модель ответа получения текущего пользователя
    """

    is_active: bool
    is_onboarded: bool
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]
    birth_date: Optional[date]
    passport_series: Optional[str]
    passport_number: Optional[str]
    type: Optional[UserType.serializer]
    interested_sub: bool

    class Config:
        orm_mode = True
