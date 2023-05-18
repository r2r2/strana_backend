from typing import Optional

from pydantic import Field

from src.users import constants as users_constants
from src.agencies import constants as agencies_constants

from ..entities import BaseAgentModel


class RequestGetMeModel(BaseAgentModel):
    """
    Модель запроса получения текущего агента
    """

    class Config:
        orm_mode = True


class _AgencyRetrieveModel(BaseAgentModel):
    """
    Модель детального агенства
    """

    id: int
    inn: Optional[str]
    city: Optional[str]
    name: Optional[str]
    type: Optional[agencies_constants.AgencyType.serializer]

    class Config:
        orm_mode = True


class ResponseUserInfoBaseModel(BaseAgentModel):
    name: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]


class ResponseGetMeModel(ResponseUserInfoBaseModel):
    """
    Модель ответа получения текущего агента
    """

    is_active: bool = Field(..., alias="isActive")
    is_approved: bool = Field(..., alias="isApproved")
    is_contracted: bool = Field(..., alias="isContracted")
    type: Optional[users_constants.UserType.serializer]

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class ResponseProfileModel(ResponseUserInfoBaseModel):
    """
    Модель ответа получения профиля текущего агента
    """

    email: Optional[str]
    phone: Optional[str]
    agency: Optional[_AgencyRetrieveModel]

    class Config:
        orm_mode = True
