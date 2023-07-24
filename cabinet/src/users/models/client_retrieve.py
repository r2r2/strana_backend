from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import root_validator, validator

from src.agencies.constants import AgencyType
from src.booking import constants as booking_constants
from src.properties.constants import PropertyTypes

from ..entities import BaseCheckModel, BaseUserModel
from src.users.repos.unique_status import IconType


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
    value: Optional[str]
    title: Optional[str]
    unique_status: Optional[Any]
    subtitle: Optional[str]
    color: Optional[str]
    background_color: Optional[str]
    border_color: Optional[str]
    icon: Optional[IconType.serializer]
    status_fixed: Optional[bool]
    requested: Optional[datetime]
    dispute_requested: Optional[datetime]

    @root_validator
    def get_unique_status(cls, values: dict[str, Any]) -> dict[str, Any]:
        """unique status"""
        if unique_status := values.pop("unique_status"):
            values["value"] = unique_status.slug
            values["title"] = unique_status.title
            values["subtitle"] = unique_status.subtitle
            values["icon"] = unique_status.icon
            values["color"] = unique_status.color
            values["background_color"] = unique_status.background_color
            values["border_color"] = unique_status.border_color
        return values

    class Config:
        orm_mode = True


class _PinningStatusModel(BaseCheckModel):
    title: Optional[str]
    value: Optional[str]
    unique_status: Optional[Any]
    subtitle: Optional[str]
    icon: Optional[IconType.serializer]
    color: Optional[str]
    background_color: Optional[str]
    border_color: Optional[str]

    @root_validator
    def get_unique_status(cls, values: dict[str, Any]) -> dict[str, Any]:
        """unique status"""
        if unique_status := values.pop("unique_status"):
            values["value"] = unique_status.slug
            values["title"] = unique_status.title
            values["subtitle"] = unique_status.subtitle
            values["icon"] = unique_status.icon
            values["color"] = unique_status.color
            values["background_color"] = unique_status.background_color
            values["border_color"] = unique_status.border_color
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
    pinning_status: Optional[_PinningStatusModel]

    agent: Optional[_AgentRetrieveModel]
    agency: Optional[_AgencyRetrieveModel]

    class Config:
        orm_mode = True
