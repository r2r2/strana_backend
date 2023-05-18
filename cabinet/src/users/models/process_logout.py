from ..entities import BaseUserModel


class RequestProcessLogoutModel(BaseUserModel):
    """
    Модель запроса процессинга выхода
    """

    class Config:
        orm_mode = True


class ResponseProcessLogoutModel(BaseUserModel):
    """
    Модель ответа процессинга выхода
    """

    class Config:
        orm_mode = True
