from datetime import date
from typing import Any, Optional

from pydantic import UUID4, validator

from common.utils import parse_phone
from ..exceptions import UserIncorrectPhoneForamtError
from ..constants import UserType
from ..entities import BaseUserModel


class RequestChangePhoneModel(BaseUserModel):
    """
    Модель запроса смены пароля
    """

    code: str
    phone: str
    token: UUID4

    @validator("phone")
    def validate_phone(cls, phone: str) -> str:
        phone: Optional[str] = parse_phone(phone)
        if not phone:
            raise UserIncorrectPhoneForamtError
        return phone

    class Config:
        orm_mode = True


class ResponseChangePhoneModel(BaseUserModel):
    """
    Модель ответа смены пароля
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
