from datetime import datetime
from typing import Any, Optional

from pydantic import root_validator
from src.agencies.constants import AgencyType
from src.users.constants import UserStatus
from src.users.entities import BaseCheckModel, BaseUserModel


class _StatusModel(BaseCheckModel):
    """Проверка полльзователя на уникальность"""
    requested: Optional[datetime]
    dispute_requested: Optional[datetime]
    status_fixed: Optional[bool]
    status: Optional[UserStatus.serializer]
    value: Optional[str]
    label: Optional[str]

    @root_validator
    def get_status(cls, values: dict[str, Any]) -> dict[str, Any]:
        """status"""
        status = values.pop("status")
        values["value"] = status.value
        values["label"] = status.label
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
