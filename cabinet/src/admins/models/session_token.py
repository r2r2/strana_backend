from typing import Optional

from ..entities import BaseAdminModel


class RequestSessionTokenModel(BaseAdminModel):
    """
    Модель запроса токена в сессии
    """

    class Config:
        orm_mode = True


class ResponseSessionTokenModel(BaseAdminModel):
    """
    Модель ответа токена в сессии
    """

    role: Optional[str]
    token: Optional[str]
    type: Optional[str]

    class Config:
        orm_mode = True
