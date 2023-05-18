from ..entities import BaseAgencyModel


class RequestAdminsAgenciesApprovalModel(BaseAgencyModel):
    """
    Модель запроса одобрения агенства администратором
    """

    is_approved: bool

    class Config:
        orm_mode = True


class ResponseAdminsAgenciesApprovalModel(BaseAgencyModel):
    """
    Модель ответа одобрения агенства администратором
    """

    class Config:
        orm_mode = True
