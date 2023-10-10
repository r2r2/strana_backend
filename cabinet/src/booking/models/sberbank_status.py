from pydantic import Field

from common.pydantic import CamelCaseBaseModel
from ..entities import BaseBookingModel


class RequestSberbankStatusModel(BaseBookingModel):
    """
    Модель запроса статуса сбербанка
    """

    class Config:
        orm_mode = True


class ResponseSberbankStatusModel(BaseBookingModel):
    """
    Модель ответа статуса сбербанка
    """

    class Config:
        orm_mode = True


class ResponseSberbankExtendedStatusModel(BaseBookingModel, CamelCaseBaseModel):
    """
    Модель расширенного ответа статуса сбербанка
    """

    booking_id: int = Field(alias="bookingId")
    status: str
    is_fast_booking: bool
    action_code_description: str

    class Config:
        orm_mode = True
