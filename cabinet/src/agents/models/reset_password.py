from ..entities import BaseAgentModel


class RequestResetPasswordModel(BaseAgentModel):
    """
    Модель запроса письма редиректа сброса
    """

    class Config:
        orm_mode = True


class ResponseResetPasswordModel(BaseAgentModel):
    """
    Модель ответа письма редиректа сброса
    """

    class Config:
        orm_mode = True
