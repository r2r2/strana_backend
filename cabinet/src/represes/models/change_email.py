from ..entities import BaseRepresModel


class RequestChangeEmailModel(BaseRepresModel):
    """
    Модель запроса смены почты
    """

    class Config:
        orm_mode = True


class ResponseChangeEmailModel(BaseRepresModel):
    """
    Модель ответа смены почты
    """

    class Config:
        orm_mode = True
