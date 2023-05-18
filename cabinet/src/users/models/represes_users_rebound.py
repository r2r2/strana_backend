from ..entities import BaseUserModel


class RequestRepresesUsersReboundModel(BaseUserModel):
    """
    Модель запроса перепривязки пользователя представителем агенства
    """

    to_agent_id: int
    from_agent_id: int

    class Config:
        orm_mode = True


class ResponseRepresesUsersReboundModel(BaseUserModel):
    """
    Модель ответ перепривязки пользователя представителем агенства
    """

    class Config:
        orm_mode = True
