from ..entities import BaseUserModel


class RequestAgentsUsersUnboundModel(BaseUserModel):
    """
    Модель запроса отвязки пользователя агента
    """

    class Config:
        orm_mode = True


class ResponseAgentsUsersUnboundModel(BaseUserModel):
    """
    Модель ответ отвязки пользователя агента
    """

    class Config:
        orm_mode = True
