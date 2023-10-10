from typing import Optional

from pydantic import Field, root_validator, validator

from common.pydantic import СhangeableGetterDict
from src.users import constants as users_constants
from src.agencies import constants as agencies_constants

from ..entities import BaseRepresModel


class RequestGetMeModel(BaseRepresModel):
    """
    Модель запроса получения текущего представителя
    """

    class Config:
        orm_mode = True


class _AgencyRetrieveModel(BaseRepresModel):
    """
    Модель детального агенства
    """

    id: int
    inn: Optional[str]
    city: Optional[str]
    name: Optional[str]
    type: Optional[agencies_constants.AgencyType.serializer]
    general_type: dict | None = Field(default=None, alias="generalType")

    @validator('general_type')
    def validate_from_id(cls, v):
        return v.get('slug')

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class Loyalty(BaseRepresModel):
    point: int | None
    label: str | None
    icon: dict | None
    levelIcon: dict | None
    background: dict | None


class ResponseUserInfoBaseModel(BaseRepresModel):
    name: str | None
    surname: str | None
    patronymic: str | None
    agency: _AgencyRetrieveModel | None
    is_fired: bool | None = Field(default=None, alias="isFired")
    loyalty: Loyalty | None = None

    @root_validator(pre=True)
    def get_loyalty(cls, values: dict) -> dict:
        if values.get("loyalty_status_name"):
            loyalty_dict = dict(
                point=values.get("loyalty_point_amount"),
                label=values.get("loyalty_status_name"),
                icon=values.get("loyalty_status_icon"),
                levelIcon=values.get("loyalty_status_level_icon"),
                background=values.get("loyalty_status_icon_profile"),
            )
            values["loyalty"] = loyalty_dict
        return values

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        getter_dict = СhangeableGetterDict


class ResponseGetMeModel(BaseRepresModel):
    """
    Модель ответа получения текущего представителя
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
