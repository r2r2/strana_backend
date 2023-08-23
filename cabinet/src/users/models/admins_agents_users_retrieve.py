from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Union, Any

from pydantic import root_validator, validator

from src.booking import constants as booking_constants
from src.properties.constants import PropertyTypes

from ..entities import BaseUserModel


class RequestAdminsAgentsUsersRetrieveModel(BaseUserModel):
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


class _AgencyRetrieveModel(BaseUserModel):
    """
    Модель агенства пользователя агента
    """

    id: Optional[int]
    name: Optional[str]

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


class _CheckRetrieveModel(BaseUserModel):
    """
    Модель проверки пользователя агента
    """

    agent_id: Optional[int]
    unique_status: Optional[Any]

    class Config:
        orm_mode = True


class ResponseAdminsAgentsUsersRetrieveModel(BaseUserModel):
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
    status: Optional[Any]

    # Totally overrided fields
    checks: Optional[list[_CheckRetrieveModel]]

    @root_validator
    def get_agency(cls, values: dict[str, Any]) -> dict[str, Any]:
        agency: Union[_AgencyRetrieveModel, None] = values.get("agency")
        if agency:
            agency: str = agency.name
        else:
            agency = None
        values["agency"]: Union[str, None] = agency
        return values

    @root_validator
    def get_status(cls, values: dict[str, Any]) -> dict[str, Any]:
        checks: Union[list[Any], None] = values.pop("checks", None)
        if checks:
            check: _CheckRetrieveModel = checks[0]
            status: dict[str, Any] = {
                "value": check.unique_status.slug,
                "label": f"{check.unique_status.title} {check.unique_status.subtitle or ''}".strip(),
            }
        else:
            status = None
        values["status"]: Union[dict[str, Any], None] = status
        return values

    class Config:
        orm_mode = True

        @staticmethod
        def schema_extra(schema: dict[str, Any]) -> None:
            schema["properties"].pop("checks")
