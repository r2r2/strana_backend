from typing import Optional

from ..entities import BaseAgentModel


class RequestSessionTokenModel(BaseAgentModel):
    """
    Модель запроса токена в сессии
    """

    class Config:
        orm_mode = True


class ResponseSessionTokenModel(BaseAgentModel):
    """
    Модель ответа токена в сессии
    """

    role: Optional[str]
    token: Optional[str]
    type: Optional[str]

    class Config:
        orm_mode = True
