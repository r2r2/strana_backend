from typing import Optional, Literal

from pydantic import EmailStr, constr, validator

from common.utils import parse_phone
from ..entities import BaseAdminModel
from ..exceptions import AdminIncorrectPhoneFormat


class RequestProcessAdminRegisterModel(BaseAdminModel):
    """
    Модель запроса регистрации администратора
    """

    phone: str
    password: str
    email: EmailStr
    name: constr(max_length=50)
    surname: constr(max_length=50)
    patronymic: Optional[constr(max_length=50)]

    @validator('phone')
    def validate_phone(cls, phone: str) -> str:
        phone: Optional[str] = parse_phone(phone)
        if phone is None:
            raise AdminIncorrectPhoneFormat
        return phone

    class Config:
        orm_mode = True


class ResponseProcessRegisterModel(RequestProcessAdminRegisterModel):
    """
    Модель ответа регистрации администратора
    """
    phone: str
    email: EmailStr
    name: str
    surname: str
    patronymic: str

    class Config:
        orm_mode = True
