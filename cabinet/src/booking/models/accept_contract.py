from datetime import datetime
from typing import Optional

from ..entities import BaseBookingModel


class RequestAcceptContractModel(BaseBookingModel):
    """
    Модель запроса принятия договора
    """

    property_id: Optional[str]
    booking_type_id: Optional[int]
    contract_accepted: bool
    booking_id: Optional[int]

    class Config:
        orm_mode = True


class ResponseAcceptContractModel(BaseBookingModel):
    """
    Модель ответа принятия договора
    """

    id: int
    created: Optional[datetime]
    expires: Optional[datetime]

    class Config:
        orm_mode = True


class RequestFastAcceptContractModel(BaseBookingModel):
    """
    Модель запроса принятия договора для быстрой брони
    """

    booking_id: int
    contract_accepted: bool

    class Config:
        orm_mode = True
