from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import validator
from src.agencies.models import AgencyRetrieveModel
from src.agents.models import AgentRetrieveModel
from src.booking.constants import (BookingCreatedSources, BookingStages,
                                   BookingSubstages)
from src.properties.models import PropertyRetrieveModel

from ..entities import BaseBookingModel


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


class _BookingStatusListModel(BaseBookingModel):
    """
    Модель статуса списка бронирований
    """

    name: Optional[str]

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
    booking_tags: Optional[list[BookingTagListModel]]

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
    created_source: Optional[BookingCreatedSources.serializer]

    agent: Optional[AgentRetrieveModel]
    agency: Optional[AgencyRetrieveModel]

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
