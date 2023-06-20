from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, root_validator
from pytz import UTC

from src.properties.models import PropertyRetrieveModel
from ...agencies.models import AgencyRetrieveModel
from ...agents.models import AgentRetrieveModel
from ...projects.models.projects_list import ProjectListModel
from ..constants import UserStatus, UserPinningStatusType
from ..entities import BaseUserModel


class _CheckListModel(BaseUserModel):
    """
    Модель проверки пользователя
    """

    status: Optional[UserStatus.serializer]
    comment: Optional[str]
    requested: date

    class Config:
        orm_mode = True


class _StatusModel(BaseUserModel):
    """
    Проверка пользователя на уникальность
    """
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


class _PinningStatusModel(BaseUserModel):
    status: Optional[UserPinningStatusType.serializer]
    label: Optional[str]
    value: Optional[str]

    @root_validator
    def get_pinning_status(cls, values: dict[str, Any]) -> dict[str, Any]:
        """set pinning status"""
        if pinning_status := values.pop("status"):
            values["label"] = pinning_status.label
            values["value"] = pinning_status.value
        else:
            values["label"] = UserPinningStatusType.to_label(UserPinningStatusType.UNKNOWN)
            values["value"] = UserPinningStatusType.to_value(UserPinningStatusType.UNKNOWN)
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
