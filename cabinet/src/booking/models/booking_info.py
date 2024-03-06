from decimal import Decimal
from typing import Any

from pydantic import root_validator

from src.properties.constants import PropertyTypes
from src.booking.entities import BaseBookingModel


class ProjectBookingInfoModel(BaseBookingModel):
    """
    Модель проекта инфо бронирования.
    """

    id: int
    name: str | None
    city: Any | None

    @root_validator
    def validate_city(cls, values: dict[str, Any]) -> dict[str, Any]:
        city = values.pop('city', None)
        values['city'] = city.name if city else None
        return values

    class Config:
        orm_mode = True


class PropertyBookingInfoModel(BaseBookingModel):
    """
    Модель объекта недвижимости инфо бронирования.
    """

    id: int
    type: PropertyTypes.serializer | None
    rooms: int | None
    
    class Config:
        orm_mode = True


class UserBookingInfoModel(BaseBookingModel):
    """
    Модель клиента инфо бронирования.
    """

    id: int
    phone: str | None
    email: str | None
    name: str | None
    surname: str | None
    patronymic: str | None

    class Config:
        orm_mode = True


class ResponseBookingInfoModel(BaseBookingModel):
    """
    Модель инфо бронирования.
    """

    id: int
    amocrm_id: int | None
    project: ProjectBookingInfoModel | None
    property: PropertyBookingInfoModel | None
    final_payment_amount: Decimal | None
    user: UserBookingInfoModel | None

    class Config:
        orm_mode = True
