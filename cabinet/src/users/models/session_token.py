from typing import Optional

from ..entities import BaseUserModel


class RequestSessionTokenModel(BaseUserModel):
    """
    Модель запроса токена в сессии
    """

    class Config:
        orm_mode = True


class ResponseSessionTokenModel(BaseUserModel):
    """
    Модель ответа токена в сессии
    """

    role: Optional[str]
    token: Optional[str]
    type: Optional[str]

    class Config:
        orm_mode = True
