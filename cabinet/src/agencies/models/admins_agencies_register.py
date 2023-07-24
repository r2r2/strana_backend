from pydantic import constr, EmailStr, validator

from common import wrappers
from typing import Optional, Literal

from common.files.models import FileCategoryListModel
from common.utils import parse_phone
from ..constants import AgencyType
from ..entities import BaseAgencyModel
from ..exceptions import AgencyIncorrectPhoneForamtError


@wrappers.as_form
class RequestAdminsAgenciesRegisterModel(BaseAgencyModel):
    """
    Модель запроса регистрации агенства администратором
    """

    inn: str
    city: str
    phone: str
    email: EmailStr
    type: Literal["OOO", "IP"]
    name: constr(max_length=50)
    naming: constr(max_length=50)
    surname: constr(max_length=50)
    patronymic: Optional[constr(max_length=50)]
    duty_type: Literal["director", "brand_manager", "building_manager", "building_leader"]

    @validator('phone')
    def validate_phone(cls, phone: str) -> str:
        phone: Optional[str] = parse_phone(phone)
        if phone is None:
            raise AgencyIncorrectPhoneForamtError
        return phone

    @validator("city", pre=True)
    def get_city_name(cls, value):
        if value:
            return value.name
        return None

    class Config:
        orm_mode = True


class ResponseAdminsAgenciesRegisterModel(BaseAgencyModel):
    """
    Модель ответа регистрации агенства администратором
    """

    id: int
    inn: Optional[str]
    city: Optional[str]
    type: Optional[AgencyType.serializer]
    files: Optional[list[FileCategoryListModel]]

    @validator("city", pre=True)
    def get_city_name(cls, value):
        if value:
            return value.name
        return None

    class Config:
        orm_mode = True
