from datetime import datetime

from pydantic import Field

from ..entities import BaseBookingModel, BaseBookingCamelCaseBaseModel


class RequestBookingPaymentConditionsModel(BaseBookingModel):
    """
    Модель запроса выбора условий оплаты
    """
    booking_type_id: int = Field(alias="bookingType")


class ResponseBookingPaymentConditionsModel(BaseBookingCamelCaseBaseModel):
    """
    Модель ответа выбора условий оплаты
    """
    id: int = Field(alias="bookingId")
    booking_period: int
    payment_amount: int
    until: datetime
    condition_chosen: bool
