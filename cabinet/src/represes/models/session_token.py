from typing import Optional

from ..entities import BaseRepresModel


class RequestSessionTokenModel(BaseRepresModel):
    """
    Модель запроса токена в сессии
    """

    class Config:
        orm_mode = True


class ResponseSessionTokenModel(BaseRepresModel):
    """
    Модель ответа токена в сессии
    """

    role: Optional[str]
    token: Optional[str]
    type: Optional[str]

    class Config:
        orm_mode = True
