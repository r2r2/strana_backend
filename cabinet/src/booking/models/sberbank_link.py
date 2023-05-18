from ..entities import BaseBookingModel
from ..constants import PaymentView


class RequestSberbankLinkModel(BaseBookingModel):
    """
    Модель запроса ссылки сбербанка
    """

    payment_page_view: PaymentView.validator

    class Config:
        orm_mode = True


class ResponseSberbankLinkModel(BaseBookingModel):
    """
    Модель ответа ссылки сбербанка
    """

    payment_url: str

    class Config:
        orm_mode = True
