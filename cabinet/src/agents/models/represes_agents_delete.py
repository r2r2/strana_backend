from ..entities import BaseAgentModel


class RequestRepresesAgentsDeleteModel(BaseAgentModel):
    """
    Модель запроса удаления агента представителем агенства
    """

    class Config:
        orm_mode = True


class ResponseRepresesAgentsDeleteModel(BaseAgentModel):
    """
    Модель ответа удаления агента представителем агенства
    """

    class Config:
        orm_mode = True
