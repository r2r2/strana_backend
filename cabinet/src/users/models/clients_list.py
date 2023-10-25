from datetime import datetime
from typing import Any, Optional

from pydantic import root_validator
from src.agencies.constants import AgencyType
from src.users.entities import BaseCheckModel, BaseUserModel


class _StatusModel(BaseCheckModel):
    """Проверка полльзователя на уникальность"""
    requested: Optional[datetime]
    dispute_requested: Optional[datetime]
    status_fixed: Optional[bool]
    unique_status: Optional[Any]
    value: Optional[str]
    title: Optional[str]
    subtitle: Optional[str]
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
            values["color"] = unique_status.color
            values["background_color"] = unique_status.background_color
            values["border_color"] = unique_status.border_color
        return values

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


class _AgencyRetrieveModel(BaseUserModel):
    """
    Модель агенства пользователя агента
    """

    id: Optional[int]
    name: Optional[str]
    type: Optional[AgencyType.serializer]

    class Config:
        orm_mode = True


class _PinningStatusModel(BaseCheckModel):
    title: Optional[str]
    value: Optional[str]
    unique_status: Optional[Any]
    subtitle: Optional[str]
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
            values["color"] = unique_status.color
            values["background_color"] = unique_status.background_color
            values["border_color"] = unique_status.border_color
        return values

    class Config:
        orm_mode = True


class _ClientsListModel(BaseUserModel):
    """Модель ответа клиента"""
    id: int
    amocrm_id: Optional[int]
    name: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]
    phone: Optional[str]
    email: Optional[str]

    status: Optional[_StatusModel]
    pinning_status: Optional[_PinningStatusModel] | None

    bookings_count: int = 0
    bookings_list: Any
    active_bookings_count: int = 0
    successful_bookings_count: int = 0
    unsuccessful_bookings_count: int = 0

    agent: Optional[_AgentRetrieveModel]
    agency: Optional[_AgencyRetrieveModel]

    class Config:
        orm_mode = True


class ResponseClientsListModel(BaseUserModel):
    """
    Модель ответа списка пользователей представителя агенства
    """

    count: int
    page_info: dict[str, Any]
    result: list[_ClientsListModel]

    class Config:
        orm_mode = True
