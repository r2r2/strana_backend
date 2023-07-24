from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, root_validator

from src.properties.models import PropertyRetrieveModel
from ...agencies.models import AgencyRetrieveModel
from ...agents.models import AgentRetrieveModel
from ...projects.models.projects_list import ProjectListModel
from src.users.constants import UserStatus
from src.users.entities import BaseUserModel, BaseCheckModel


class _CheckListModel(BaseUserModel):
    """
    Модель проверки пользователя
    """

    status: Optional[UserStatus.serializer]
    comment: Optional[str]
    requested: date

    class Config:
        orm_mode = True


class _StatusModel(BaseCheckModel):
    """
    Проверка пользователя на уникальность
    """
    requested: Optional[datetime]
    dispute_requested: Optional[datetime]
    status_fixed: Optional[bool]
    value: Optional[str]
    title: Optional[str]
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


class _BookingUserModel(BaseUserModel):
    id: int
    name: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    work_end: Optional[date]
    work_start: Optional[date]
    status: Optional[_StatusModel]
    pinning_status: Optional[_PinningStatusModel]

    class Config:
        orm_mode = True


class AmoCRMAction(BaseModel):
    id: Optional[int]
    name: Optional[str]
    slug: Optional[str]
    role_id: Optional[int]


class AmoCRMStatus(BaseModel):
    id: int
    group_id: Optional[int]
    name: Optional[str]
    color: Optional[str]
    show_reservation_date: Optional[bool]
    show_booking_date: Optional[bool]
    steps_numbers: Optional[int]
    current_step: Optional[int]
    actions: Optional[list[AmoCRMAction]]

    class Config:
        orm_mode = True


class ButtonAction(BaseModel):
    type: str
    id: str

    class Config:
        orm_mode = True


class Button(BaseModel):
    label: str
    type: str
    action: ButtonAction

    class Config:
        orm_mode = True


class TaskInstanceResponseSchema(BaseModel):
    type: str
    title: str
    hint: Optional[str]
    text: str
    buttons: Optional[list[Button]]

    class Config:
        orm_mode = True


class _BookingBuildingRetrieveModel(BaseUserModel):
    """
    Модель корпуса детального бронирования
    """

    name: Optional[str]
    address: Optional[str]
    built_year: Optional[int]
    total_floor: Optional[int]
    ready_quarter: Optional[int]

    class Config:
        orm_mode = True


class _UserBookingsListModel(BaseUserModel):
    """
    Модель сделки
    """
    id: int
    amocrm_id: Optional[int]

    payment_amount: Optional[Decimal]
    final_payment_amount: Optional[Decimal]
    expires: Optional[datetime]
    until: Optional[datetime]

    user: _BookingUserModel

    commission_value: Optional[int]
    commission: Optional[Decimal]

    agent: Optional[AgentRetrieveModel]
    agency: Optional[AgencyRetrieveModel]
    amocrm_status: Optional[AmoCRMStatus]
    project: Optional[ProjectListModel]
    building: Optional[_BookingBuildingRetrieveModel]
    property: Optional[PropertyRetrieveModel]
    tags: Optional[list[str]]
    tasks: Optional[list[TaskInstanceResponseSchema]]

    class Config:
        orm_mode = True


class ResponseUserResponseBookingRetrieve(_UserBookingsListModel):
    """
    Модель карточки бронирования
    """

    created: Optional[datetime]


class ResponseBookingsUsersListModel(BaseUserModel):
    """
    Модель ответа списка пользователей администратором
    """

    count: int
    page_info: dict[str, Any]
    result: list[_UserBookingsListModel]

    class Config:
        orm_mode = True
