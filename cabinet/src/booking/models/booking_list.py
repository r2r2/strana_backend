from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional, Any

from pydantic import validator, root_validator, parse_obj_as
from src.agencies.models import AgencyRetrieveModel
from src.agents.models import AgentRetrieveModel
from src.booking.constants import (BookingCreatedSources, BookingStages,
                                   BookingSubstages)
from src.properties.models import PropertyRetrieveModel

from src.booking.entities import BaseBookingModel, BaseBookingCamelCaseModel
from src.task_management.constants import TaskStatusType


class _BookingFloorListModel(BaseBookingModel):
    """
    Модель этажа списка бронирований
    """

    number: Optional[int]

    class Config:
        orm_mode = True


class _BookingBuildingListModel(BaseBookingModel):
    """
    Модель корпуса списка бронирований
    """

    name: Optional[str]
    address: Optional[str]
    built_year: Optional[int]
    total_floor: Optional[int]
    ready_quarter: Optional[int]

    class Config:
        orm_mode = True


class _BookingProjectListModel(BaseBookingModel):
    """
    Модель проекта списка бронирований
    """

    name: Optional[str]
    slug: Optional[str]

    class Config:
        orm_mode = True


class AmoCRMAction(BaseBookingCamelCaseModel):
    id: Optional[int]
    name: Optional[str]
    slug: Optional[str]
    role_id: Optional[int]


class _BookingStatusListModel(BaseBookingCamelCaseModel):
    """
    Модель статуса списка бронирований
    """
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


class BookingTagListModel(BaseBookingModel):
    """
    Модель тега списка бронирований
    """

    label: str
    style: str
    slug: str

    @validator("style", pre=True)
    def get_style(cls, style) -> str:
        return str(style)

    class Config:
        orm_mode = True


class BookingListFilters(BaseBookingModel):
    project_id: Optional[int]
    property_id: Optional[int]
    agent_id: Optional[int]


class ButtonAction(BaseBookingCamelCaseModel):
    type: str
    id: str

    class Config:
        orm_mode = True


class Button(BaseBookingCamelCaseModel):
    label: str
    type: str
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
    current_step: str | None
    buttons: Optional[list[Button]]

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


class _BookingSourceSchema(BaseBookingCamelCaseModel):
    slug: str
    name: str
    value: Optional[str]
    label: Optional[str]

    @root_validator
    def build_response(cls, values: dict[str, Any]) -> dict[str, Any]:
        values['value'] = values.pop('slug')
        values['label'] = values.pop('name')
        return values

    class Config:
        orm_mode = True


class _ClientAmocrmGroupStatusSchema(BaseBookingCamelCaseModel):
    id: int
    name: str
    is_final: bool
    is_current: bool
    show_reservation_date: bool
    show_booking_date: bool
    tags: list[BookingTagListModel | None]

    class Config:
        orm_mode = True


class PaymentMethodModel(BaseBookingCamelCaseModel):
    """
    Модель способов оплаты
    """

    id: Optional[int]
    amocrm_id: Optional[int]
    name: Optional[str]
    slug: Optional[str]

    class Config:
        orm_mode = True


class MortgageTypeModel(BaseBookingCamelCaseModel):
    """
    Модель типа ипотеки
    """

    id: Optional[int]
    amocrm_id: Optional[int]
    title: Optional[str]
    by_dev: Optional[bool]
    slug: Optional[str]

    class Config:
        orm_mode = True


class _BookingListModel(BaseBookingModel):
    """
    Модель бронирования
    """

    id: int

    price_payed: bool
    params_checked: bool
    personal_filled: bool
    contract_accepted: bool
    bill_paid: bool
    online_purchase_started: bool
    payment_method_selected: bool
    amocrm_agent_data_validated: bool
    ddu_created: bool
    amocrm_ddu_uploaded_by_lawyer: bool
    ddu_accepted: bool
    escrow_uploaded: bool
    amocrm_signing_date_set: bool
    amocrm_signed: bool
    amocrm_status: Optional[_BookingStatusListModel]
    client_group_statuses: list[_ClientAmocrmGroupStatusSchema | None]
    booking_tags: Optional[list[BookingTagListModel]]
    amo_payment_method: PaymentMethodModel | None
    mortgage_type: MortgageTypeModel | None

    origin: Optional[str]
    until: Optional[datetime]
    created: Optional[datetime]
    expires: Optional[datetime]
    floor: Optional[_BookingFloorListModel]
    project: Optional[_BookingProjectListModel]
    building: Optional[_BookingBuildingListModel]
    property: Optional[PropertyRetrieveModel]
    amocrm_stage: Optional[BookingStages.serializer]
    amocrm_substage: Optional[BookingSubstages.serializer]
    final_payment_amount: Optional[Decimal]
    payment_amount: Optional[Decimal]
    created_source: Optional[Any]

    agent: Optional[AgentRetrieveModel]
    agency: Optional[AgencyRetrieveModel]
    tasks: Optional[list[TaskInstanceResponseSchema]]

    # Method fields
    current_step: Optional[int]
    continue_link: Optional[str]
    is_fast_booking: bool

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

    @root_validator
    def build_response(cls, values: dict[str, Any]):
        booking_source = values.pop('booking_source', None)
        if booking_source:
            values['created_source'] = parse_obj_as(_BookingSourceSchema, booking_source)
        return values

    @validator("is_fast_booking", pre=True, always=True)
    def get_is_fast_booking(cls, is_fast_booking) -> bool:
        return is_fast_booking()

    @validator("current_step", pre=True, always=True)
    def get_current_step(cls, current_step) -> int:
        return current_step()

    @validator("continue_link", pre=True, always=True)
    def get_continue_link(cls, continue_link) -> str:
        return continue_link()

    class Config:
        orm_mode = True

    @validator("online_purchase_step", pre=True, always=True)
    def get_online_purchase_step(cls, online_purchase_step) -> str:
        return online_purchase_step()


class MortgageBookingListModel(_BookingListModel):
    """
    Модель бронирования для ипотеки
    """

    is_eligible_for_mortgage: bool
    has_subsidy_price: bool | None
    client_group_statuses: list | None


class RequestBookingListModel(BaseBookingModel):
    """
    Модель запроса списка бронирований
    """

    class Config:
        orm_mode = True


class ResponseBookingListModel(BaseBookingModel):
    """
    Модель ответа списка бронирований
    """

    count: int
    result: list[_BookingListModel]

    class Config:
        orm_mode = True
