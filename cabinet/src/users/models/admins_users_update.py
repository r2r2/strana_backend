from typing import Optional, Any, Union

from pydantic import constr, validator

from ..entities import BaseUserModel
from ..mixins.validators import CleanNoneValidatorMixin


class RequestAdminsUsersUpdateModel(BaseUserModel, CleanNoneValidatorMixin):
    """
    Модель запроса обновления пользователя администратором
    """

    name: Optional[constr(max_length=50)]
    surname: Optional[constr(max_length=50)]
    patronymic: Optional[constr(max_length=50)]
    agent_id: Optional[int]
    agency_id: Optional[int]

    @validator("agency_id")
    def validate_agency(
        cls, value: Optional[int], values: dict[str, Any], **kwargs: Any
    ) -> Union[int, None]:
        if value and not values.get("agent_id"):
            raise ValueError("No agent sent")
        return value

    class Config:
        orm_mode = True


class ResponseAdminsUsersUpdateModel(BaseUserModel):
    """
    Модель ответа запроса обновления пользователя 
    """

    class Config:
        orm_mode = True
