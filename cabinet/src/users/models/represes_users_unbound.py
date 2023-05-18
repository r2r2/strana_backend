from ..entities import BaseUserModel


class RequestRepresesUsersUnboundModel(BaseUserModel):
    """
    Модель запроса отвязки пользователя представителем агенства
    """

    agent_id: int

    class Config:
        orm_mode = True


class ResponseRepresesUsersUnboundModel(BaseUserModel):
    """
    Модель ответ отвязки пользователя представителем агенства
    """

    class Config:
        orm_mode = True
