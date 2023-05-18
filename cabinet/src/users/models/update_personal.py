from datetime import date
from typing import Optional
from pydantic import EmailStr, constr

from ..entities import BaseUserModel
from ..constants import UserType


class RequestUpdatePersonalModel(BaseUserModel):
    """
    Модель запроса обновления персональный данных
    """

    email: EmailStr
    birth_date: date
    name: constr(max_length=50)
    surname: constr(max_length=50)
    patronymic: Optional[constr(max_length=50)]
    passport_series: constr(max_length=4, min_length=4)
    passport_number: constr(max_length=6, min_length=6)

    class Config:
        orm_mode = True


class ResponseUpdatePersonalModel(BaseUserModel):
    """
    Модель ответа обновления персональных данных
    """
    is_active: bool
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]
    birth_date: Optional[date]
    passport_series: Optional[str]
    passport_number: Optional[str]
    type: Optional[UserType.serializer]

    class Config:
        orm_mode = True
