from ..entities import BaseBookingModel


class RequestSingleEmailModel(BaseBookingModel):
    """
    Модель запроса одиночного письма
    """

    class Config:
        orm_mode = True


class ResponseSingleEmailModel(BaseBookingModel):
    """
    Модель ответа одиночного письма
    """

    class Config:
        orm_mode = True