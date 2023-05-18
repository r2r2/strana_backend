from ..entities import BaseRepresModel


class RequestResetPasswordModel(BaseRepresModel):
    """
    Модель запроса письма редиректа сброса
    """

    class Config:
        orm_mode = True


class ResponseResetPasswordModel(BaseRepresModel):
    """
    Модель ответа письма редиректа сброса
    """

    class Config:
        orm_mode = True
