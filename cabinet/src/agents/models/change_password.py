from pydantic import Field

from common.security.models import PasswordModel
from ..entities import BaseAgentModel


class RequestChangePasswordModel(PasswordModel):
    """
    Модель запроса сброса пароля
    """
    password_1: str = Field(..., alias="password1")
    password_2: str = Field(..., alias="password2")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class ResponseChangePasswordModel(BaseAgentModel):
    """
    Модель ответа сброса пароля
    """

    id: int

    class Config:
        orm_mode = True
