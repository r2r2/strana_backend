from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import validator

from src.booking.entities import BaseBookingModel


class BookingModel(BaseBookingModel):
    id: int
    online_purchase_step: Optional[str]


class PropertyModel(BaseBookingModel):
    area: Optional[Decimal]
    rooms: Optional[int]

    class Config:
        orm_mode = True


class UserModel(BaseBookingModel):
    name: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]

    class Config:
        orm_mode = True


class DocumentsModel(BaseBookingModel):
    name: str
    size: int
    url: str

    class Config:
        orm_mode = True


class BookingHistoryModel(BaseBookingModel):
    id: int
    booking: Optional[BookingModel]
    message: str
    property: Optional[PropertyModel]
    created_at: datetime
    user: Optional[UserModel]
    documents: list[list[DocumentsModel]]

    class Config:
        orm_mode = True


class ResponseBookingHistoryModel(BaseBookingModel):
    next_page: bool
    results: list[BookingHistoryModel]

    class Config:
        orm_mode = True
