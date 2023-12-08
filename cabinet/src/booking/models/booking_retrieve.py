from datetime import date, datetime
from decimal import Decimal
from typing import Any, Awaitable, Literal, Optional

from pydantic import constr, root_validator, validator, parse_obj_as

from common.files.models import FileCategoryListModel
from src.agencies.models import AgencyRetrieveModel
from src.agents.models import AgentRetrieveModel
from src.properties.models import PropertyRetrieveModel
from src.booking.entities import BaseBookingModel, BaseBookingCamelCaseModel
from src.task_management.constants import TaskStatusType, ButtonCondition

from ..constants import (
    BookingCreatedSources,
    BookingSubstages,
    BookingStages,
    MaritalStatus,
    # PaymentMethods,
    RelationStatus,
)


class _BookingProjectRetrieveModel(BaseBookingModel):
    """
    Модель проекта детального бронирования
    """

    name: Optional[str]
    slug: Optional[str]
    city: Optional[Any]

    @root_validator
    def validate_city(cls, values: dict[str, Any]) -> dict[str, Any]:
        city = values.pop("city", None)
        values["city"] = city.slug if city else None
        return values

    class Config:
        orm_mode = True


class _BookingBuildingRetrieveModel(BaseBookingModel):
    """
    Модель корпуса детального бронирования
    """

    name: str | None
    address: str | None
    built_year: str | None
    total_floor: str | None
    ready_quarter: str | None

    class Config:
        orm_mode = True


class _BookingFloorRetrieveModel(BaseBookingModel):
    """
    Модель этажа детального бронирования
    """

    number: str | None

    class Config:
        orm_mode = True


class BookingTagRetrieveModel(BaseBookingModel):
    """
    Модель тега бронирований
    """

    label: str
    style: str
    slug: str

    @validator("style", pre=True)
    def get_style(cls, style) -> str:
        return str(style)

    class Config:
        orm_mode = True


class _DDUParticipant(BaseBookingModel):
    id: int
    name: str
    surname: str
    patronymic: str
    inn: str | None
    passport_serial: str | None
    passport_number: str | None
    passport_issued_by: str | None
    passport_department_code: str | None
    passport_issued_date: date | None
    relation_status: Optional[RelationStatus.serializer]
    marital_status: Optional[MaritalStatus.serializer]
    is_not_resident_of_russia: bool
    is_older_than_fourteen: bool | None
    has_children: bool
    files: list[FileCategoryListModel]

    class Config:
        orm_mode = True


class _BookingDDURetrieveModel(BaseBookingModel):
    """
    Модель объекта ДДУ детального бронирования
    """

    account_number: constr(max_length=50)
    payees_bank: str
    bik: str
    corresponding_account: str
    bank_inn: str
    bank_kpp: str
    participants: list[_DDUParticipant]
    change_diffs: list | None
    files: list[FileCategoryListModel]

    @validator("participants", pre=True, always=True)
    def get_participants(cls, participants):
        return [_DDUParticipant.from_orm(participant) for participant in participants]

    class Config:
        orm_mode = True


class RequestBookingRetrieveModel(BaseBookingModel):
    """
    Модель запроса детального бронирования
    """

    class Config:
        orm_mode = True


class ButtonAction(BaseBookingCamelCaseModel):
    type: str
    id: str
    condition: ButtonCondition.serializer | None

    @root_validator
    def validate_condition(cls, values):
        if condition := values.get("condition"):
            values["condition"] = condition.value
        else:
            values.pop("condition")
        return values

    class Config:
        orm_mode = True


class Button(BaseBookingCamelCaseModel):
    label: str
    type: str
    slug_step: str | None
    action: ButtonAction

    class Config:
        orm_mode = True


class TaskInstanceResponseSchema(BaseBookingCamelCaseModel):
    id: int
    type: str
    title: str
    hint: str | None
    text: str
    is_main: bool
    task_status: str | None
    current_step: str | None
    buttons: list[Button] | None
    buttons_detail_view: list[Button] | None
    systems: list[str] | None

    class Config:
        orm_mode = True


class TaskStatusSchema(BaseBookingCamelCaseModel):
    name: str
    description: str
    type: TaskStatusType.serializer
    priority: int
    slug: str

    class Config:
        orm_mode = True


class AmoCRMAction(BaseBookingCamelCaseModel):
    id: int | None
    name: str | None
    slug: str | None
    role_id: int | None


class _BookingStatusListModel(BaseBookingCamelCaseModel):
    """
    Модель статуса списка бронирований
    """

    id: int | None
    group_id: int | None
    name: str | None
    color: str | None
    show_reservation_date: bool | None
    show_booking_date: bool | None
    steps_numbers: int | None
    current_step: int | None
    actions: list[AmoCRMAction] | None

    class Config:
        orm_mode = True


class _BookingSourceSchema(BaseBookingCamelCaseModel):
    slug: str | None
    name: str | None
    value: str | None
    label: str | None

    @root_validator
    def build_response(cls, values: dict[str, Any]) -> dict[str, Any]:
        values["value"] = values.pop("slug", None)
        values["label"] = values.pop("name", None)
        return values

    class Config:
        orm_mode = True


class ResponseBookingRetrieveModel(BaseBookingModel):
    """
    Модель ответа детального бронирования
    """

    id: int

    price_payed: bool
    booking_period: int | None
    max_booking_period: int | None
    params_checked: bool
    personal_filled: bool
    contract_accepted: bool
    online_purchase_started: bool
    payment_method_selected: bool
    amocrm_agent_data_validated: bool
    ddu_created: bool
    amocrm_ddu_uploaded_by_lawyer: bool
    ddu_accepted: bool
    escrow_uploaded: bool
    amocrm_signing_date_set: bool
    amocrm_signed: bool
    has_subsidy_price: bool = False
    amocrm_status: _BookingStatusListModel | None

    origin: str | None
    until: datetime | None
    created: datetime | None
    expires: datetime | None
    payment_url: Optional[str]
    payment_amount: Optional[Decimal]
    final_payment_amount: Optional[Decimal]

    floor: Optional[_BookingFloorRetrieveModel]
    project: Optional[_BookingProjectRetrieveModel]
    building: Optional[_BookingBuildingRetrieveModel]
    property: Optional[PropertyRetrieveModel]
    ddu: Optional[_BookingDDURetrieveModel]
    amocrm_stage: Optional[BookingStages.serializer]
    amocrm_substage: Optional[BookingSubstages.serializer]
    booking_tags: Optional[list[BookingTagRetrieveModel]]

    maternal_capital: bool
    housing_certificate: bool
    government_loan: bool
    client_has_an_approved_mortgage: Optional[bool]
    bank_contact_info_id: Optional[int]
    mortgage_request_id: Optional[int]
    ddu_id: Optional[int]
    signing_date: Optional[date]
    created_source: Optional[BookingCreatedSources.serializer]
    booking_source: Optional[Any]

    files: Optional[list[FileCategoryListModel]]

    agent: Optional[AgentRetrieveModel]
    agency: Optional[AgencyRetrieveModel]
    tasks: Optional[list[TaskInstanceResponseSchema]]

    # Method fields
    current_step: Optional[int]
    continue_link: Optional[str]
    is_fast_booking: bool
    condition_chosen: bool
    is_can_pay: bool

    online_purchase_step: Optional[
        Literal[
            "online_purchase_start",
            "payment_method_select",
            "amocrm_agent_data_validation",
            "ddu_create",
            "amocrm_ddu_uploading_by_lawyer",
            "ddu_accept",
            "escrow_upload",
            "amocrm_signing_date",
            "amocrm_signing",
            "finished",
        ]
    ]

    @validator("is_fast_booking", pre=True, always=True)
    def get_is_fast_booking(cls, is_fast_booking) -> bool:
        return is_fast_booking()

    @validator("current_step", pre=True, always=True)
    def get_current_step(cls, current_step) -> int:
        return current_step()

    @validator("continue_link", pre=True, always=True)
    def get_continue_link(cls, continue_link) -> str:
        return continue_link()

    @validator("online_purchase_step", pre=True, always=True)
    def get_online_purchase_step(cls, online_purchase_step) -> str:
        return online_purchase_step()

    @validator("is_can_pay", pre=True, always=True)
    def get_is_can_pay(cls, is_can_pay) -> bool:
        return is_can_pay()

    @validator("ddu", pre=True, always=True)
    def get_ddu(cls, ddu):
        if isinstance(ddu, Awaitable) or ddu is None or ddu.pk is None:
            return None
        return ddu

    @root_validator
    def build_response(cls, values: dict[str, Any]):
        booking_source = values.pop("booking_source", None)
        if booking_source:
            values["created_source"] = parse_obj_as(
                _BookingSourceSchema, booking_source
            )
        return values

    class Config:
        orm_mode = True
