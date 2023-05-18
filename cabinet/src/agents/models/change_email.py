from ..entities import BaseAgentModel


class RequestChangeEmailModel(BaseAgentModel):
    """
    Модель запроса смены почты
    """

    class Config:
        orm_mode = True


class ResponseChangeEmailModel(BaseAgentModel):
    """
    Модель ответа смены почты
    """

    class Config:
        orm_mode = True
