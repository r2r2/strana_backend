from datetime import date
from typing import Optional

from pydantic import UUID4, validator

from common.utils import parse_phone
from ..exceptions import UserIncorrectPhoneFormatError
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
            raise UserIncorrectPhoneFormatError
        return phone

    class Config:
        orm_mode = True


class ResponseChangePhoneModel(BaseUserModel):
    """
    Модель ответа смены пароля
    """

    is_active: bool
    name: str | None
    email: str | None
    phone: str | None
    surname: str | None
    patronymic: str | None
    birth_date: Optional[date]
    passport_series: str | None
    passport_number: str | None
    type: UserType.serializer | None

    class Config:
        orm_mode = True
