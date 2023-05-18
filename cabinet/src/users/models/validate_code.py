from typing import Any, Optional

from pydantic import UUID4, validator

from common.utils import parse_phone
from ..entities import BaseUserModel
from ..exceptions import UserIncorrectPhoneForamtError


class RequestValidateCodeModel(BaseUserModel):
    """
    Модель запроса отправки кода
    """

    phone: str
    token: UUID4
    code: str

    @validator("phone")
    def validate_phone(cls, phone: str) -> str:
        phone: Optional[str] = parse_phone(phone)
        if not phone:
            raise UserIncorrectPhoneForamtError
        return phone

    class Config:
        orm_mode = True


class ResponseValidateCodeModel(BaseUserModel):
    """
    Модель ответа отправки кода
    """

    role: Optional[str]
    token: Optional[str]
    type: Optional[str]

    class Config:
        orm_mode = True
