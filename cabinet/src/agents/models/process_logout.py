from ..entities import BaseAgentModel


class RequestProcessLogoutModel(BaseAgentModel):
    """
    Модель запроса процессинга выхода
    """

    class Config:
        orm_mode = True


class ResponseProcessLogoutModel(BaseAgentModel):
    """
    Модель ответа процессинга выхода
    """

    class Config:
        orm_mode = True
