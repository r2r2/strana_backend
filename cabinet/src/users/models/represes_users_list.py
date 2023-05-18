# pylint: disable=redefined-builtin

from datetime import date
from decimal import Decimal
from typing import Any, Optional, Union

from common.utils import get_hyperlink
from pydantic import root_validator as method_field

from ..constants import UserStatus
from ..entities import BaseUserModel


class RequestRepresesUsersListModel(BaseUserModel):
    """
    Модель запроса списка пользователей представителя агенства
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


class _CheckListModel(BaseUserModel):
    """
    Модель проверки пользователя
    """

    status: Optional[UserStatus.serializer]

    class Config:
        orm_mode = True


class _UserListModel(BaseUserModel):
    """
    Модель пользователя представителя агенства
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

    # Method fields
    status: Optional[UserStatus.serializer]

    # Totally overrided fields
    checks: Optional[list[_CheckListModel]]

    # Hyperlinks
    hyper_info: Optional[dict[str, Any]]

    @method_field
    def get_status(cls, values: dict[str, Any]) -> dict[str, Any]:
        """get status"""
        checks: Union[list[Any], None] = values.pop("checks", None)
        if checks:
            status: dict[str, Any] = checks[0].status.dict()
        else:
            status = None
        values["status"]: Union[dict[str, Any], None] = status
        return values

    @method_field
    def get_hyper_info(cls, values: dict[str, Any]) -> dict[str, Any]:
        "get hyper info"
        id: int = values.get("id")
        agent: Union[_AgentListModel, None] = values.get("agent")
        values["hyper_info"]: dict[str, Any] = dict(
            retrieve=get_hyperlink(f"/users/repres/clients/{id}"),
            agents_retrieve=get_hyperlink(f"/users/repres/clients/{agent.id}/{id}") if agent else None,
        )
        return values

    class Config:
        orm_mode = True

        @staticmethod
        def schema_extra(schema: dict[str, Any]) -> None:
            schema["properties"].pop("checks")


class ResponseRepresesUsersListModel(BaseUserModel):
    """
    Модель ответа списка пользователей представителя агенства
    """

    count: int
    page_info: dict[str, Any]
    result: list[_UserListModel]

    class Config:
        orm_mode = True
