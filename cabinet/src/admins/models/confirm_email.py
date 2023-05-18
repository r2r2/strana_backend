from ..entities import BaseAdminModel


class RequestConfirmEmailModel(BaseAdminModel):
    """
    Модель запроса подтверждения почты
    """

    class Config:
        orm_mode = True


class ResponseConfirmEmailModel(BaseAdminModel):
    """
    Модель ответа подтверждения почты
    """

    class Config:
        orm_mode = True
