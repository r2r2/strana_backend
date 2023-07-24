from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Union, Any

from pydantic import root_validator as method_field, validator

from src.booking import constants as booking_constants
from src.properties.constants import PropertyTypes

from ..constants import UserStatus
from ..entities import BaseUserModel


class RequestRepresesAgentsUsersRetrieveModel(BaseUserModel):
    """
    Модель запроса детального пользователя агента
    """

    class Config:
        orm_mode = True


class _InterestedFloorListModel(BaseUserModel):
    """
    Модель этажа интересующего объекта пользователя
    """

    id: int
    number: Optional[str]

    class Config:
        orm_mode = True


class _InterestedProjectListModel(BaseUserModel):
    """
    Модель проекта интересующего объекта пользователя
    """

    id: int
    slug: Optional[str]
    name: Optional[str]

    class Config:
        orm_mode = True


class _InterestedPropertyListModel(BaseUserModel):
    """
    Модель объекта интересующего объекта пользователя
    """

    id: int
    plan: Optional[str]
    price: Optional[int]
    rooms: Optional[int]
    number: Optional[str]
    article: Optional[str]
    area: Optional[Decimal]
    plan_png: Optional[str]
    original_price: Optional[int]

    class Config:
        orm_mode = True


class _InterestedBuildingListModel(BaseUserModel):
    """
    Модель корпуса интересующего объекта пользователя
    """

    id: int
    name: Optional[str]

    class Config:
        orm_mode = True


class _IndentFloorListModel(BaseUserModel):
    """
    Модель этажа забронированного объекта пользователя
    """

    id: int
    number: Optional[str]

    class Config:
        orm_mode = True


class _IndentProjectListModel(BaseUserModel):
    """
    Модель проекта забронированного объекта пользователя
    """

    id: int
    slug: Optional[str]
    name: Optional[str]
    city: Optional[str]

    @validator("city", pre=True)
    def get_city_name(cls, value):
        if value:
            return value.name
        return None

    class Config:
        orm_mode = True


class _IndentPropertyListModel(BaseUserModel):
    """
    Модель объекта забронированного объекта пользователя
    """

    id: int
    plan: Optional[str]
    price: Optional[int]
    rooms: Optional[int]
    number: Optional[str]
    article: Optional[str]
    area: Optional[Decimal]
    plan_png: Optional[str]
    original_price: Optional[int]
    type: Optional[PropertyTypes.serializer]

    class Config:
        orm_mode = True


class _IndentBuildingListModel(BaseUserModel):
    """
    Модель корпуса забронированного объекта пользователя
    """

    id: int
    name: Optional[str]

    class Config:
        orm_mode = True


class _InterestedListModel(BaseUserModel):
    """
    Модель интересующего объекта пользователя
    """

    floor: Optional[_InterestedFloorListModel]
    project: Optional[_InterestedProjectListModel]
    property: Optional[_InterestedPropertyListModel]
    building: Optional[_InterestedBuildingListModel]

    class Config:
        orm_mode = True


class _IndentListModel(BaseUserModel):
    """
    Модель бронирования пользователя
    """

    decremented: bool
    until: Optional[datetime]
    expires: Optional[datetime]
    commission: Optional[Decimal]
    decrement_reason: Optional[str]
    commission_value: Optional[Decimal]
    amocrm_stage: Optional[booking_constants.BookingStages.serializer]
    amocrm_substage: Optional[booking_constants.BookingSubstages.serializer]

    floor: Optional[_IndentFloorListModel]
    project: Optional[_IndentProjectListModel]
    property: Optional[_IndentPropertyListModel]
    building: Optional[_IndentBuildingListModel]

    class Config:
        orm_mode = True


class _AgentRetrieveModel(BaseUserModel):
    """
    Модель агента пользователя представителя агенства
    """

    id: Optional[int]
    name: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]

    class Config:
        orm_mode = True


class _AgencyRetrieveModel(BaseUserModel):
    """
    Модель агенства пользователя агента
    """

    id: Optional[int]
    name: Optional[str]

    class Config:
        orm_mode = True


class _CheckRetrieveModel(BaseUserModel):
    """
    Модель проверки пользователя агента
    """

    agent_id: Optional[int]
    status: Optional[UserStatus.serializer]

    class Config:
        orm_mode = True


class ResponseRepresesAgentsUsersRetrieveModel(BaseUserModel):
    """
    Модель ответа детального пользователя агента
    """

    id: int
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    surname: Optional[str]
    work_end: Optional[date]
    patronymic: Optional[str]
    work_start: Optional[date]
    agent: Optional[_AgentRetrieveModel]
    indents: Optional[list[_IndentListModel]]
    interesting: Optional[list[_InterestedListModel]]

    # Method fields
    agency: Optional[_AgencyRetrieveModel]
    status: Optional[UserStatus.serializer]

    # Totally overrided fields
    checks: Optional[list[_CheckRetrieveModel]]

    @method_field
    def get_agency(cls, values: dict[str, Any]) -> dict[str, Any]:
        agency: Union[_AgencyRetrieveModel, None] = values.get("agency")
        if agency:
            agency: str = agency.name
        else:
            agency = None
        values["agency"]: Union[str, None] = agency
        return values

    @method_field
    def get_status(cls, values: dict[str, Any]) -> dict[str, Any]:
        checks: Union[list[Any], None] = values.pop("checks", None)
        if checks:
            status: dict[str, Any] = checks[0].status.dict()
        else:
            status = None
        values["status"]: Union[dict[str, Any], None] = status
        return values

    class Config:
        orm_mode = True

        @staticmethod
        def schema_extra(schema: dict[str, Any]) -> None:
            schema["properties"].pop("checks")
