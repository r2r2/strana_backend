from ..entities import BaseRepresModel


class RequestResetAvailableModel(BaseRepresModel):
    """
    Модель запроса доступности сброса пароля
    """

    class Config:
        orm_mode = True


class ResponseResetAvailableModel(BaseRepresModel):
    """
    Модель ответа доступности сброса пароля
    """

    available: bool

    class Config:
        orm_mode = False
