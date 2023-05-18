from common.security.models import PasswordModel
from ..entities import BaseAdminModel


class RequestChangePasswordModel(BaseAdminModel, PasswordModel):
    """
    Модель запроса сброса пароля
    """

    class Config:
        orm_mode = True


class ResponseChangePasswordModel(BaseAdminModel):
    """
    Модель ответа сброса пароля
    """

    id: int

    class Config:
        orm_mode = True
