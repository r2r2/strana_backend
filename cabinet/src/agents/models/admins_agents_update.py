from typing import Optional
from pydantic import EmailStr, constr, validator

from common.utils import parse_phone
from ..entities import BaseAgentModel
from ..exceptions import AgentIncorrectPhoneForamtError
from ...users.mixins.validators import CleanNoneValidatorMixin


class RequestAdminsAgentsUpdateModel(BaseAgentModel, CleanNoneValidatorMixin):
    """
    Модель запроса изменения агента администратором
    """

    phone: Optional[str]
    email: Optional[EmailStr]
    name: Optional[constr(max_length=50)]
    surname: Optional[constr(max_length=50)]
    patronymic: Optional[constr(max_length=50)]

    @validator('phone')
    def validate_phone(cls, phone: str) -> str:
        phone: Optional[str] = parse_phone(phone)
        if phone is None:
            raise AgentIncorrectPhoneForamtError
        return phone

    class Config:
        orm_mode = True


class ResponseAdminsAgentsUpdateModel(BaseAgentModel):
    """
    Модель ответа изменения агента администратором
    """

    class Config:
        orm_mode = True
