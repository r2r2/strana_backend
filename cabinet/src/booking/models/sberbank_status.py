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
