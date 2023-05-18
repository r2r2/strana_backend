from ..entities import BaseAgentModel


class RequestConfirmEmailModel(BaseAgentModel):
    """
    Модель запроса подтверждения почты
    """

    class Config:
        orm_mode = True


class ResponseConfirmEmailModel(BaseAgentModel):
    """
    Модель ответа подтверждения почты
    """

    class Config:
        orm_mode = True
