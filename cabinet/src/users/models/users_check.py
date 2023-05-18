from datetime import datetime
from typing import Optional

from common.utils import parse_phone
from pydantic import EmailStr, constr, validator

from ..constants import UserStatus
from ..entities import BaseUserModel
from ..exceptions import UserIncorrectPhoneForamtError


class RequestUsersCheckModel(BaseUserModel):
    """
    Модель запроса проверки пользователя агентом на уникальность
    """

    phone: constr(min_length=9)
    email: Optional[EmailStr]
    name: Optional[constr(max_length=50)]
    surname: Optional[constr(max_length=50)]
    patronymic: Optional[constr(max_length=50)]

    @validator('phone')
    def validate_phone(cls, phone: str) -> str:
        """
        Валидация номера телефона
        """
        phone: Optional[str] = parse_phone(phone)
        if not phone:
            raise UserIncorrectPhoneForamtError
        return phone

    class Config:
        orm_mode = True


class ResponseUsersCheckModel(BaseUserModel):
    """
    Модель ответа проверки пользователя агентом на уникальность
    """

    id: Optional[int]
    user_id: Optional[int]
    agent_id: Optional[int]
    agency_id: Optional[int]
    requested: Optional[datetime]
    status: Optional[UserStatus.serializer]

    class Config:
        orm_mode = True
