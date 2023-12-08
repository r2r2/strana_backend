from ..entities import BaseRepresModel


class RequestSessionTokenModel(BaseRepresModel):
    """
    Модель запроса токена в сессии
    """

    class Config:
        orm_mode = True
