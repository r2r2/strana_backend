from typing import Optional

from common.security.models import PasswordModel
from ..entities import BaseAdminModel


class RequestSetPasswordModel(BaseAdminModel, PasswordModel):
    """
    Модель запроса установки пароля
    """

    is_contracted: Optional[bool] = False

    class Config:
        orm_mode = True


class ResponseSetPasswordModel(BaseAdminModel):
    """
    Модель ответа установки пароля
    """

    id: int
    email: str

    class Config:
        orm_mode = True
