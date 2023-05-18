from ..entities import BaseAgentModel


class RequestConfirmPhoneModel(BaseAgentModel):
    """
    Модель запроса подтверждения телефона
    """

    class Config:
        orm_mode = True


class ResponseConfirmPhoneModel(BaseAgentModel):
    """
    Модель ответа подтверждения телефона
    """

    class Config:
        orm_mode = True
