from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional

from common.pydantic import CamelCaseBaseModel
from pydantic import BaseModel, root_validator, validator, Field
from src.meetings.constants import MeetingPropertyType, MeetingType
from src.properties.models import PropertyRetrieveModel
from src.users.constants import UserStatus
from src.users.entities import BaseCheckModel, BaseUserModel

from ...agencies.models import AgencyRetrieveModel
from ...agents.models import AgentRetrieveModel
from ...booking.models.booking_retrieve import BookingTagRetrieveModel
from ...projects.models.projects_list import ProjectListModel


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

        # @staticmethod
        # def schema_extra(schema: dict[str, Any]) -> None:
        #     schema["properties"].pop("unique_status")


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

        # @staticmethod
        # def schema_extra(schema: dict[str, Any]) -> None:
        #     schema["properties"].pop("unique_status")


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


class MeetingSchema(CamelCaseBaseModel):
    id: int
    city: Optional[str]
    project: Optional[str]
    property_type: MeetingPropertyType.serializer
    type: MeetingType.serializer
    date: str
    time: str
    address: Optional[str]
    link: Optional[str]
    slug: Optional[str]

    @validator("type")
    def validate_type(cls, value: MeetingType) -> str:
        return value.value

    class Config:
        orm_mode = True


class FixationSchema(CamelCaseBaseModel):
    fixation_expires: Optional[datetime]
    days_before_fixation_expires: Optional[int]
    extension_number: Optional[int]

    class Config:
        orm_mode = True


class TaskInstanceResponseSchema(BaseModel):
    type: str
    title: str
    hint: Optional[str]
    text: str
    buttons: Optional[list[Button]]
    meeting: Optional[MeetingSchema]
    fixation: Optional[FixationSchema]

    class Config:
        orm_mode = True

    def dict(self, *args, **kwargs):
        original_dict = super().dict(*args, **kwargs)
        return {
            key: value for key, value in original_dict.items()
            if key != "meeting" or value is not None
        }


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
    final_discount: Optional[Decimal]
    final_additional_options: Optional[Decimal]
    expires: Optional[datetime]
    fixation_expires: Optional[datetime] = Field(None, alias="fixationExpires")
    until: Optional[datetime]

    user: _BookingUserModel

    commission_value: Optional[int]
    commission: Optional[Decimal]

    agent: Optional[AgentRetrieveModel]
    agency: Optional[AgencyRetrieveModel]
    amocrm_status: Optional[AmoCRMStatus]
    booking_tags: Optional[list[BookingTagRetrieveModel]]
    project: Optional[ProjectListModel]
    building: Optional[_BookingBuildingRetrieveModel]
    property: Optional[PropertyRetrieveModel]
    tags: Optional[list[str]]
    tasks: Optional[list[TaskInstanceResponseSchema]]

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


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
