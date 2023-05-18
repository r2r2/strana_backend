from typing import Optional, Any

from pydantic import constr, EmailStr, validator

from common.utils import parse_phone
from ..exceptions import AgentIncorrectPhoneForamtError
from ..entities import BaseAgentModel


class RequestRepresesAgentsRegisterModel(BaseAgentModel):
    """
    Модель запроса регистрации агента представителем агенства
    """

    phone: str
    email: EmailStr
    name: constr(max_length=50)
    surname: constr(max_length=50)
    patronymic: Optional[constr(max_length=50)]

    @validator("phone")
    def validate_phone(cls, phone: str) -> str:
        phone: Optional[str] = parse_phone(phone)
        if phone is None:
            raise AgentIncorrectPhoneForamtError
        return phone

    class Config:
        orm_mode = True


class ResponseRepresesAgentsRegisterModel(BaseAgentModel):
    """
    Модель ответа регистрации агента представителем агенства
    """

    id: int
    name: Optional[str]
    phone: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]

    class Config:
        orm_mode = True
