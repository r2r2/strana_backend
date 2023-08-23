import binascii
from datetime import datetime, date
from decimal import Decimal
from typing import Any, Optional

from pydantic import root_validator, validator, Field

from common.utils import from_global_id
from src.agencies.models import AgencyRetrieveModel
from src.agents.models import AgentRetrieveModel
from src.properties.constants import PropertyTypes

from ..constants import (MeetingPropertyType, MeetingTopicType,
                         MeetingType)
from ..entities import BaseMeetingModel


class PropertyFloorModel(BaseMeetingModel):
    """
    Модель этажа интересующего объекта пользователя для карточки встречи.
    """

    id: Optional[int]
    number: Optional[str]

    class Config:
        orm_mode = True


class PropertyRetrieveModel(BaseMeetingModel):
    """
    Модель объекта недвижимости для карточки встречи.
    """

    id: int
    price: Optional[int]
    rooms: Optional[int]
    number: Optional[str]
    article: Optional[str]
    area: Optional[Decimal]
    discount: Optional[int]
    global_id: Optional[str]
    backend_id: Optional[int]
    original_price: Optional[int]
    final_price: Optional[int]
    plan: Optional[dict[str, Any]]
    plan_png: Optional[dict[str, Any]]
    floor: Optional[PropertyFloorModel]
    type: Optional[PropertyTypes.serializer]

    @root_validator
    def decode_backend_id(cls, values: dict) -> dict:
        """Parse backend property_id from global_id"""

        try:
            _, values['backend_id'] = from_global_id(values.get('global_id'))
        except (binascii.Error, AttributeError):
            pass
        return values

    class Config:
        orm_mode = True


class AmoCRMAction(BaseMeetingModel):
    id: Optional[int]
    name: Optional[str]
    slug: Optional[str]
    role_id: Optional[int]

    class Config:
        orm_mode = True


class AmoCRMStatus(BaseMeetingModel):
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


class ButtonAction(BaseMeetingModel):
    type: str
    id: str

    class Config:
        orm_mode = True


class Button(BaseMeetingModel):
    label: str
    type: str
    action: ButtonAction

    class Config:
        orm_mode = True


class MeetingSchema(BaseMeetingModel):
    id: int
    city: Optional[str]
    project: Optional[str]
    property_type: MeetingPropertyType.serializer
    type: MeetingType.serializer
    date: str
    time: str

    @validator("type")
    def validate_type(cls, value: MeetingType) -> str:
        return value.value

    class Config:
        orm_mode = True


class TaskInstanceResponseSchema(BaseMeetingModel):
    type: str
    title: str
    hint: Optional[str]
    text: str
    buttons: Optional[list[Button]]
    meeting: Optional[MeetingSchema]

    class Config:
        orm_mode = True


class StatusModel(BaseMeetingModel):
    """
    Проверка пользователя на уникальность для карточки встречи.
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


class PinningStatusModel(BaseMeetingModel):
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


class BookingUserModel(BaseMeetingModel):
    id: int
    name: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    work_end: Optional[date]
    work_start: Optional[date]
    status: Optional[StatusModel]
    pinning_status: Optional[PinningStatusModel]

    class Config:
        orm_mode = True


class BookingDetailMeetingModel(BaseMeetingModel):
    """
    Модель бронирования карточки встречи.
    """

    id: int
    amocrm_id: int
    amocrm_status: Optional[AmoCRMStatus]
    user: Optional[BookingUserModel]
    agent: Optional[AgentRetrieveModel]
    agency: Optional[AgencyRetrieveModel]
    property: Optional[PropertyRetrieveModel]
    tasks: Optional[list[TaskInstanceResponseSchema]]

    class Config:
        orm_mode = True


class ResponseStatusMeetingModel(BaseMeetingModel):
    """
    Модель бронирования
    """

    slug: str = Field(..., alias="value")
    label: str

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class ResponseDetailMeetingModel(BaseMeetingModel):
    """
    Модель карточки встречи.
    """
    id: int
    title: Optional[str]
    city_id: int
    project_id: Optional[int]
    booking: Optional[BookingDetailMeetingModel]
    status: ResponseStatusMeetingModel
    record_link: Optional[str]
    meeting_link: Optional[str]
    meeting_address: Optional[str]
    topic: MeetingTopicType.serializer
    type: MeetingType.serializer
    property_type: MeetingPropertyType.serializer
    date: datetime
    steps_numbers: Optional[int]
    current_step: Optional[int]

    class Config:
        orm_mode = True

    @validator('date')
    def validate_date(cls, date: datetime) -> str:
        return date.strftime("%Y-%m-%dT%H:%M")

    @root_validator
    def get_title(cls, values: dict[str, Any]) -> dict[str, Any]:
        """
        Получение информации для заголовка карточки встречи.
        """
        booking: dict = values.get("booking")
        if user := booking.user:
            user_fio_surname = user.surname if user.surname else ''
            user_fio_name = (user.name[0] + ".") if user.name else ""
            user_fio_patronymic = (user.patronymic[0] + ".") if user.patronymic else ""
            values["title"]: str = f"Встреча с {user_fio_surname} {user_fio_name}{user_fio_patronymic}"
        return values

