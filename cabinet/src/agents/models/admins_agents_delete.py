from ..entities import BaseAgentModel


class RequestAdminsAgentsDeleteModel(BaseAgentModel):
    """
    Модель запроса удаления агента администратором
    """

    class Config:
        orm_mode = True


class ResponseAdminsAgentsDeleteModel(BaseAgentModel):
    """
    Модель ответа удаления агента администратором
    """

    class Config:
        orm_mode = True
