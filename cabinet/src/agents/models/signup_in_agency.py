from typing import Optional

from pydantic import Field, validator

from common.pydantic import CamelCaseBaseModel
from src.agencies import constants as agencies_constants
from src.users import constants as users_constants

from ..entities import BaseAgentModel


class _AgencyRetrieveModel(BaseAgentModel):
    """
    Модель детального агенства.
    """

    id: int
    inn: Optional[str]
    city: Optional[str]
    name: Optional[str]
    type: Optional[agencies_constants.AgencyType.serializer]

    @validator("city", pre=True)
    def get_city_name(cls, value):
        if value:
            return value.name
        return None

    class Config:
        orm_mode = True


class ResponseSignupInAgencyModel(BaseAgentModel):
    """
    Модель ответа для восстановления агента в новом агентстве.
    """

    name: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]
    is_active: bool = Field(..., alias="isActive")
    is_approved: bool = Field(..., alias="isApproved")
    is_contracted: bool = Field(..., alias="isContracted")
    type: Optional[users_constants.UserType.serializer]
    agency: Optional[_AgencyRetrieveModel]
    is_fired: Optional[bool]

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class RequestSignupInAgencyModel(CamelCaseBaseModel):
    """
    Модель запроса для восстановления агента в новом агентстве.
    """

    agency_inn: str
