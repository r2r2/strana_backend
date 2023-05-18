from ..entities import BaseBookingModel


class RequestMassEmailModel(BaseBookingModel):
    """
    Модель запроса массовых писем
    """

    class Config:
        orm_mode = True


class ResponseMassEmailModel(BaseBookingModel):
    """
    Модель ответа массовых писем
    """
    class Config:
        orm_mode = True