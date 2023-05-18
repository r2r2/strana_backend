from ..entities import BaseUserModel


class RequestRepresesUsersBoundModel(BaseUserModel):
    """
    Модель запроса привязки пользователя представителем агенства
    """

    agent_id: int

    class Config:
        orm_mode = True


class ResponseRepresesUsersBoundModel(BaseUserModel):
    """
    Модель ответ привязки пользователя представителем агенства
    """

    class Config:
        orm_mode = True
