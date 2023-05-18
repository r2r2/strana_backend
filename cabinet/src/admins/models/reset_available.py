from ..entities import BaseAdminModel


class RequestResetAvailableModel(BaseAdminModel):
    """
    Модель запроса доступности сброса пароля
    """

    class Config:
        orm_mode = True


class ResponseResetAvailableModel(BaseAdminModel):
    """
    Модель ответа доступности сброса пароля
    """

    available: bool

    class Config:
        orm_mode = False
