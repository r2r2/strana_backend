from datetime import date
from typing import Optional
from pydantic import EmailStr, constr

from ..entities import BaseUserModel
from ..constants import UserType
from ..mixins.validators import CleanNoneValidatorMixin


class RequestPartialUpdateModel(BaseUserModel, CleanNoneValidatorMixin):
    """
    Модель запроса частичного обновления
    """

    email: Optional[EmailStr]
    birth_date: Optional[date]
    is_onboarded: Optional[bool]
    name: Optional[constr(max_length=50)]
    surname: Optional[constr(max_length=50)]
    patronymic: Optional[constr(max_length=50)]
    passport_series: Optional[constr(max_length=4, min_length=4)]
    passport_number: Optional[constr(max_length=6, min_length=6)]
    interested_sub: Optional[bool]

    class Config:
        orm_mode = True


class ResponsePartialUpdateModel(BaseUserModel):
    """
    Модель ответа частичного обновления
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
