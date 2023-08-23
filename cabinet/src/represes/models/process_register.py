from typing import Optional, Any, Literal
from pydantic import constr, EmailStr, validator

from common.security.models import PasswordModel
from common.utils import parse_phone
from src.users import constants as users_constants

from ..exceptions import RepresIncorrectPhoneFormatError
from ..entities import BaseRepresModel
from ...agencies.constants import AgencyType


class RepresRegisterModel(BaseRepresModel, PasswordModel):
    name: constr(max_length=50)
    surname: constr(max_length=50)
    patronymic: Optional[constr(max_length=50)]
    duty_type: users_constants.DutyType.validator

    phone: str
    email: EmailStr
    is_contracted: bool

    @validator("phone")
    def validate_phone(cls, phone: str) -> str:
        phone: Optional[str] = parse_phone(phone)
        if phone is None:
            raise RepresIncorrectPhoneFormatError
        return phone

    class Config:
        orm_mode = True


class AgencyRegisterModel(BaseRepresModel):
    """
    Модель запроса создания агенства
    """

    inn: str
    city: str
    type: Literal["OOO", "IP"]
    name: constr(max_length=50)

    class Config:
        orm_mode = True


class RequestProcessRegisterModel(BaseRepresModel):
    """
    Модель запроса регистрации
    """

    repres: RepresRegisterModel
    agency: AgencyRegisterModel

    class Config:
        orm_mode = True


class ResponseAgencyRegisterModel(BaseRepresModel):
    id: int
    inn: Optional[str]
    city: Optional[str]
    type: Optional[AgencyType.serializer]

    class Config:
        orm_mode = True


class ResponseRepresRegisterModel(BaseRepresModel):
    id: int
    is_approved: bool

    class Config:
        orm_mode = True


class ResponseProcessRegisterModel(BaseRepresModel):
    """
    Модель ответа регистрации
    """

    agency: ResponseAgencyRegisterModel
    repres: ResponseRepresRegisterModel

    class Config:
        orm_mode = True
