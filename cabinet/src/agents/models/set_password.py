from typing import Optional

from common.security.models import PasswordModel
from ..entities import BaseAgentModel


class RequestSetPasswordModel(BaseAgentModel, PasswordModel):
    """
    Модель запроса установки пароля
    """

    is_contracted: Optional[bool] = False

    class Config:
        orm_mode = True


class ResponseSetPasswordModel(BaseAgentModel):
    """
    Модель ответа установки пароля
    """

    id: int
    is_approved: bool

    class Config:
        orm_mode = True
