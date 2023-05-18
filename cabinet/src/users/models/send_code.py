import re
from typing import Optional

from common.utils import parse_phone
from pydantic import UUID4, validator

from ..entities import BaseUserModel
from ..exceptions import UserIncorrectPhoneForamtError


class RequestSendCodeModel(BaseUserModel):
    """
    Модель запроса отправки кода
    """

    phone: str
    imgcode: Optional[str]
    userip: Optional[str]

    @validator('phone')
    def validate_phone(cls, phone: str) -> str:
        """Валидация номера телефона"""
        phone: str = parse_phone(phone)
        if re.compile(r'^(8|\+7)\d{10}$').match(phone):
            return phone
        raise UserIncorrectPhoneForamtError

    class Config:
        orm_mode = True


class ResponseSendCodeModel(BaseUserModel):
    """
    Модель ответа отправки кода
    """

    token: UUID4

    class Config:
        orm_mode = True
