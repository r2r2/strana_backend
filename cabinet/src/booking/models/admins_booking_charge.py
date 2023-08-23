from typing import Optional

from pydantic import condecimal, constr

from ..entities import BaseBookingModel


class RequestAdminsBookingChargeModel(BaseBookingModel):
    """
    Модель запроса изменения комиссии бронирования
    """

    commission: condecimal(decimal_places=2)
    decrement_reason: Optional[constr(max_length=300)]

    class Config:
        orm_mode = True


class ResponseAdminsBookingChargeModel(BaseBookingModel):
    """
    Модель ответа изменения комиссии бронирования
    """

    class Config:
        orm_mode = True
