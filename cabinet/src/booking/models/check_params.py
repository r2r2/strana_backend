from ..constants import PaymentView
from ..entities import BaseBookingModel


class RequestCheckParamsModel(BaseBookingModel):
    """
    Модель запроса проверки параметров бронирования
    """

    params_checked: bool
    payment_page_view: PaymentView.validator

    class Config:
        orm_mode = True


class ResponseCheckParamsModel(BaseBookingModel):
    """
    Модель ответа проверки параметров бронирования
    """

    id: int
    payment_url: str

    class Config:
        orm_mode = True
