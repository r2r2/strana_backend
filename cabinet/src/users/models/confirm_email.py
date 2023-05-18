from ..entities import BaseUserModel


class RequestConfirmEmailModel(BaseUserModel):
    """
    Модель запроса подтверждения почты
    """

    class Config:
        orm_mode = True


class ResponseConfirmEmailModel(BaseUserModel):
    """
    Модель ответа подтверждения почты
    """

    class Config:
        orm_mode = True