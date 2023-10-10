from hmac import compare_digest

from pydantic import constr, EmailStr, validator

from common.utils import parse_phone
from ..entities import BaseAgentModel
from ..exceptions import AgentPasswordsDoesntMatch, AgentIncorrectPhoneForamtError


class RequestProcessRegisterModel(BaseAgentModel):
    """
    Модель запроса регистрации
    """

    name: constr(max_length=50)
    surname: constr(max_length=50)
    patronymic: constr(max_length=50) | None

    phone: constr(min_length=10)
    password_1: constr(min_length=8)
    password_2: constr(min_length=8)
    email: EmailStr
    is_contracted: bool

    agency: int

    @validator("password_2")
    def validate_password(cls, password_2, values) -> str:
        password_1: str = values.get("password_1")
        if not compare_digest(password_1, password_2):
            raise AgentPasswordsDoesntMatch
        return password_1

    @validator("phone")
    def validate_phone(cls, phone: str) -> str:
        phone: str | None = parse_phone(phone)
        if phone is None:
            raise AgentIncorrectPhoneForamtError
        return phone

    class Config:
        orm_mode = True


class ResponseProcessRegisterModel(BaseAgentModel):
    """
    Модель ответа регистрации
    """

    id: int
    is_approved: bool

    class Config:
        orm_mode = True
