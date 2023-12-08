from typing import Optional, Literal

from common.utils import parse_phone
from pydantic import Field, validator, EmailStr

from ..entities import BaseUserModel
from src.users.exceptions import UserIncorrectPhoneFormat


class ResponseUserCheckUnique(BaseUserModel):
    """
    Модель ответа проверки пользователя на уникальность в базе по телефону и почте
    """

    is_unique: bool = Field(..., alias="isUnique")

    class Config:
        allow_population_by_field_name = True


class RequestUserCheckUnique(BaseUserModel):
    """
    Модель запроса проверки пользователя на уникальность в базе по телефону и почте
    """

    phone: str
    email: EmailStr
    role: Literal['agents', 'represes']

    @validator('phone')
    def validate_phone(cls, phone: str) -> str:
        phone: Optional[str] = parse_phone(phone)
        if phone is None:
            raise UserIncorrectPhoneFormat
        return phone
