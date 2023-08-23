from datetime import date, datetime
from decimal import Decimal
from typing import Any, Awaitable, Literal, Optional

from common.files.models import FileCategoryListModel
from pydantic import constr, root_validator, validator
from src.agencies.models import AgencyRetrieveModel
from src.agents.models import AgentRetrieveModel
from src.properties.models import PropertyRetrieveModel

from ..constants import (BookingCreatedSources, BookingStages,
                         BookingSubstages, MaritalStatus, PaymentMethods,
                         RelationStatus)
from ..entities import BaseBookingModel


class _BookingProjectRetrieveModel(BaseBookingModel):
    """
    Модель проекта детального бронирования
    """

    name: Optional[str]
    slug: Optional[str]
    city: Optional[Any]

    @root_validator
    def validate_city(cls, values: dict[str, Any]) -> dict[str, Any]:
        city = values.pop('city', None)
        values['city'] = city.slug if city else None
        return values

    class Config:
        orm_mode = True


class _BookingBuildingRetrieveModel(BaseBookingModel):
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


class _BookingFloorRetrieveModel(BaseBookingModel):
    """
    Модель этажа детального бронирования
    """

    number: Optional[str]

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
    inn: Optional[str]
    passport_serial: Optional[str]
    passport_number: Optional[str]
    passport_issued_by: Optional[str]
    passport_department_code: Optional[str]
    passport_issued_date: Optional[date]
    relation_status: Optional[RelationStatus.serializer]
    marital_status: Optional[MaritalStatus.serializer]
    is_not_resident_of_russia: bool
    is_older_than_fourteen: Optional[bool]
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
    change_diffs: Optional[list]
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


class ResponseBookingRetrieveModel(BaseBookingModel):
    """
    Модель ответа детального бронирования
    """

    id: int

    price_payed: bool
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

    origin: Optional[str]
    until: Optional[datetime]
    created: Optional[datetime]
    expires: Optional[datetime]
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

    payment_method: Optional[PaymentMethods.serializer]
    maternal_capital: bool
    housing_certificate: bool
    government_loan: bool
    client_has_an_approved_mortgage: Optional[bool]
    bank_contact_info_id: Optional[int]
    mortgage_request_id: Optional[int]
    ddu_id: Optional[int]
    signing_date: Optional[date]
    created_source: Optional[BookingCreatedSources.serializer]

    files: Optional[list[FileCategoryListModel]]

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

    @validator("online_purchase_step", pre=True, always=True)
    def get_online_purchase_step(cls, online_purchase_step) -> str:
        return online_purchase_step()

    @validator("ddu", pre=True, always=True)
    def get_ddu(cls, ddu):
        if isinstance(ddu, Awaitable) or ddu is None or ddu.pk is None:
            return None
        return ddu

    class Config:
        orm_mode = True
