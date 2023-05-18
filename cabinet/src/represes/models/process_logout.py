from ..entities import BaseRepresModel


class RequestProcessLogoutModel(BaseRepresModel):
    """
    Модель запроса процессинга выхода
    """

    class Config:
        orm_mode = True


class ResponseProcessLogoutModel(BaseRepresModel):
    """
    Модель ответа процессинга выхода
    """

    class Config:
        orm_mode = True
