from ..entities import BaseRepresModel


class RequestConfirmEmailModel(BaseRepresModel):
    """
    Модель запроса подтверждения почты
    """

    class Config:
        orm_mode = True


class ResponseConfirmEmailModel(BaseRepresModel):
    """
    Модель ответа подтверждения почты
    """

    class Config:
        orm_mode = True
