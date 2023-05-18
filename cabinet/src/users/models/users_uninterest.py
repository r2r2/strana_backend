from ..entities import BaseUserModel


class RequestUsersUninterestModel(BaseUserModel):
    """
    Модель запроса удаления интересующих объектов пользователю представителем агенства
    """

    uninterested: list[int]

    class Config:
        orm_mode = True


class ResponseUsersUninterestModel(BaseUserModel):
    """
    Модель ответа удаления интересующих объектов пользователю представителем агенства
    """

    id: int

    class Config:
        orm_mode = True
