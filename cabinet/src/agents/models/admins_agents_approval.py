from ..entities import BaseAgentModel


class RequestAdminsAgentsApprovalModel(BaseAgentModel):
    """
    Модель запроса одобрения агента администратором
    """

    is_approved: bool

    class Config:
        orm_mode = True


class ResponseAdminsAgentsApprovalModel(BaseAgentModel):
    """
    Модель ответа одобрения агента администратором
    """

    class Config:
        orm_mode = True
