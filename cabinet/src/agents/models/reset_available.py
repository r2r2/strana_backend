from ..entities import BaseAgentModel


class RequestResetAvailableModel(BaseAgentModel):
    """
    Модель запроса доступности сброса пароля
    """

    class Config:
        orm_mode = True


class ResponseResetAvailableModel(BaseAgentModel):
    """
    Модель ответа доступности сброса пароля
    """

    available: bool

    class Config:
        orm_mode = False
