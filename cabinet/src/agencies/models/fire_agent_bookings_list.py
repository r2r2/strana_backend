import binascii
from datetime import datetime
from decimal import Decimal
from typing import Optional, Any

from common.pydantic import CamelCaseBaseModel
from common.utils import from_global_id
from pydantic import root_validator
from src.projects.constants import ProjectStatus
from src.properties.constants import PropertyTypes

from ..entities import BaseAgencyModel


class PropertyFloorModel(BaseAgencyModel):
    """
    Модель этажа интересующего объекта пользователя
    """

    id: Optional[int]
    number: Optional[str]

    class Config:
        orm_mode = True


class PropertyRetrieveModel(CamelCaseBaseModel):
    """
    Модель объекта недвижимости
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


class _BookingUserModel(CamelCaseBaseModel):
    id: int
    name: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]
    phone: Optional[str]
    email: Optional[str]

    class Config:
        orm_mode = True


class AmoCRMAction(CamelCaseBaseModel):
    id: Optional[int]
    name: Optional[str]
    slug: Optional[str]
    role_id: Optional[int]

    class Config:
        orm_mode = True


class AmoCRMStatus(CamelCaseBaseModel):
    id: int
    name: Optional[str]
    color: Optional[str]
    steps_numbers: Optional[int]
    current_step: Optional[int]
    actions: Optional[list[AmoCRMAction]]

    class Config:
        orm_mode = True


class ProjectListModel(CamelCaseBaseModel):
    """
    Модель проекта в списке
    """

    id: int
    global_id: Optional[str]
    slug: Optional[str]
    name: Optional[str]
    city: Optional[Any]
    status: Optional[ProjectStatus.serializer]

    @root_validator
    def validate_city(cls, values: dict[str, Any]) -> dict[str, Any]:
        city = values.pop('city', None)
        values['city'] = city.slug if city else None
        return values

    class Config:
        orm_mode = True


class _FireAgentBookingsListModel(CamelCaseBaseModel):
    """
    Модель сделки.
    """

    id: int
    amocrm_id: Optional[int]
    payment_amount: Optional[Decimal]
    final_payment_amount: Optional[Decimal]
    expires: Optional[datetime]
    until: Optional[datetime]
    user: _BookingUserModel
    amocrm_status: Optional[AmoCRMStatus]
    project: Optional[ProjectListModel]
    property: Optional[PropertyRetrieveModel]

    class Config:
        orm_mode = True


class ResponseFireAgentBookingsListModel(BaseAgencyModel):
    """
    Модель ответа списка сделок при увольнении агента.
    """

    bookings: Optional[list[_FireAgentBookingsListModel]]

    class Config:
        orm_mode = True
