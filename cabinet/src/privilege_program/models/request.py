import re

from pydantic import validator, constr

from common.utils import parse_phone
from src.users.exceptions import UserIncorrectPhoneFormatError
from ..entities import BasePrivilegeCamelCaseModel


class CreatePrivilegeRequest(BasePrivilegeCamelCaseModel):
    """
    Модель запроса для создания заявки в программе привилегий
    """

    full_name: constr(min_length=1, max_length=50)
    phone: str
    email: str
    question: str

    @validator("phone")
    def validate_phone(cls, phone: str) -> str:
        """
        Валидация номера телефона
        """
        phone: str = parse_phone(phone)
        if re.compile(r"^(8|\+7)\d{10}$").match(phone):
            return phone
        raise UserIncorrectPhoneFormatError


class CreatedRequestResponse(BasePrivilegeCamelCaseModel):
    """
    Модель ответа созданной заявки
    """
    full_name: str
    phone: str
    email: str
