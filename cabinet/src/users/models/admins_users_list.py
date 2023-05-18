from datetime import date
from decimal import Decimal
from typing import Optional, Union, Any
from pydantic import root_validator as method_field


from ..constants import UserStatus
from ..entities import BaseUserModel


class RequestAdminsUsersListModel(BaseUserModel):
    """
    Модель запроса списка пользователей администратором
    """

    class Config:
        orm_mode = True


class _AgentListModel(BaseUserModel):
    """
    Модель агента пользователя
    """

    id: int
    name: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]

    class Config:
        orm_mode = True


class _AgencyListModel(BaseUserModel):
    """
    Модель агенства пользователя
    """

    id: int
    inn: Optional[str]
    name: Optional[str]

    class Config:
        orm_mode = True


class _CheckListModel(BaseUserModel):
    """
    Модель проверки пользователя
    """

    status: Optional[UserStatus.serializer]
    comment: Optional[str]

    class Config:
        orm_mode = True


class _UserListModel(BaseUserModel):
    """
    Модель пользователя администратором
    """

    id: int
    name: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    work_end: Optional[date]
    work_start: Optional[date]
    booking_count: Optional[int]
    commission_sum: Optional[int]
    is_decremented: Optional[bool]
    commission_avg: Optional[Decimal]

    agent: Optional[_AgentListModel]
    agency: Optional[_AgencyListModel]

    # Method fields
    status: Optional[UserStatus.serializer]

    # Totally overrided fields
    checks: Optional[list[_CheckListModel]]

    @method_field
    def get_status(cls, values: dict[str, Any]) -> dict[str, Any]:
        checks: Union[list[Any], None] = values.pop("checks", None)
        for check in checks[:1]:
            values["status"]: Optional[dict[str, Any]] = dict(
                comment=check.comment,
                **check.status.dict()
            )
        return values

    class Config:
        orm_mode = True

        @staticmethod
        def schema_extra(schema: dict[str, Any]) -> None:
            schema["properties"].pop("checks")


class ResponseAdminsUsersListModel(BaseUserModel):
    """
    Модель ответа списка пользователей администратором
    """

    count: int
    page_info: dict[str, Any]
    result: list[_UserListModel]

    class Config:
        orm_mode = True
