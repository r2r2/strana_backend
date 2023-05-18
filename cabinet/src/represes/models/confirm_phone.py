from ..entities import BaseRepresModel


class RequestConfirmPhoneModel(BaseRepresModel):
    """
    Модель запроса подтверждения телефона
    """

    class Config:
        orm_mode = True


class ResponseConfirmPhoneModel(BaseRepresModel):
    """
    Модель ответа подтверждения телефона
    """

    class Config:
        orm_mode = True
