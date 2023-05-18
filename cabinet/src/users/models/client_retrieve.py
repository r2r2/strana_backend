from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import root_validator as method_field
from src.agencies.constants import AgencyType
from src.booking import constants as booking_constants
from src.properties.constants import PropertyTypes

from ..constants import UserStatus
from ..entities import BaseCheckModel, BaseUserModel


class RequestAgentsUsersRetrieveModel(BaseUserModel):
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
    plan: Optional[dict[str, Any]]
    price: Optional[int]
    rooms: Optional[int]
    number: Optional[str]
    article: Optional[str]
    area: Optional[Decimal]
    plan_png: Optional[dict[str, Any]]
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
    plan: Optional[dict[str, Any]]
    price: Optional[int]
    rooms: Optional[int]
    number: Optional[str]
    article: Optional[str]
    area: Optional[Decimal]
    plan_png: Optional[dict[str, Any]]
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

    id: int
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
    type: Optional[AgencyType.serializer]

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
    email: Optional[str]
    phone: Optional[str]

    class Config:
        orm_mode = True


class _StatusModel(BaseCheckModel):
    """Проверка полльзователя на уникальность"""
    requested: Optional[datetime]
    dispute_requested: Optional[datetime]
    status_fixed: Optional[bool]
    status: Optional[UserStatus.serializer]
    value: Optional[str]
    label: Optional[str]

    @method_field
    def get_status(cls, values: dict[str, Any]) -> dict[str, Any]:
        """status"""
        status = values.pop("status")
        values["value"] = status.value
        values["label"] = status.label
        return values

    class Config:
        orm_mode = True


class ResponseClientRetrieveModel(BaseUserModel):
    """
    Модель ответа детального пользователя агента
    """

    id: int
    amocrm_id: Optional[int]
    name: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    assignation_comment: Optional[str]
    work_end: Optional[date]
    work_start: Optional[date]

    status: Optional[_StatusModel]

    agent: Optional[_AgentRetrieveModel]
    agency: Optional[_AgencyRetrieveModel]

    class Config:
        orm_mode = True
