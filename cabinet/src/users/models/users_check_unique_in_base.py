import re
from typing import Optional

from common.utils import parse_phone
from pydantic import Field, validator

from ..entities import BaseUserModel
from ..exceptions import UserIncorrectPhoneFormat, UserIncorrectEmailFormat


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
    email: str

    @validator('phone')
    def validate_phone(cls, phone: str) -> str:
        phone: Optional[str] = parse_phone(phone)
        if phone is None:
            raise UserIncorrectPhoneFormat
        return phone

    @validator('email')
    def validate_email(cls, email: str) -> str:
        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if not re.fullmatch(email_regex, email):
            raise UserIncorrectEmailFormat
        return email
