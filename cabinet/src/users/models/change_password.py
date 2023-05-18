from common.security.models import PasswordModel
from ..entities import BaseUserModel


class RequestChangePasswordModel(BaseUserModel, PasswordModel):
    """
    Модель запроса сброса пароля
    """

    class Config:
        orm_mode = True


class ResponseChangePasswordModel(BaseUserModel):
    """
    Модель ответа сброса пароля
    """

    id: int

    class Config:
        orm_mode = True
