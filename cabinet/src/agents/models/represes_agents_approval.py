from ..entities import BaseAgentModel


class RequestRepresesAgentsApprovalModel(BaseAgentModel):
    """
    Модель запроса одобрения агента представителем агенства
    """

    is_approved: bool

    class Config:
        orm_mode = True


class ResponseRepresesAgentsApprovalModel(BaseAgentModel):
    """
    Модель ответа одобрения агента представителем агенства
    """

    class Config:
        orm_mode = True
