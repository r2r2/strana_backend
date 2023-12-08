from ..entities import BaseUserModel


class RequestSessionTokenModel(BaseUserModel):
    """
    Модель запроса токена в сессии
    """

    class Config:
        orm_mode = True
