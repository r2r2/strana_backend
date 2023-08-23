from datetime import date
from decimal import Decimal
from typing import Optional, Any, Union
from pydantic import root_validator

from common.utils import get_hyperlink
from src.users.entities import BaseUserModel


class RequestAgentsUsersListModel(BaseUserModel):
    """
    Модель запроса пользователей агента
    """

    class Config:
        orm_mode = True


class _AgencyRetrieveModel(BaseUserModel):
    """
    Модель агенства пользователя агента
    """

    id: int
    name: Optional[str]

    class Config:
        orm_mode = True


class _CheckListModel(BaseUserModel):
    """
    Модель проверки пользователя агента
    """

    agent_id: Optional[int]
    unique_status: Optional[Any]

    class Config:
        orm_mode = True


class _UserListModel(BaseUserModel):
    """
    Модель пользователя агента
    """

    id: int
    name: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    surname: Optional[str]
    work_end: Optional[date]
    patronymic: Optional[str]
    work_start: Optional[date]
    booking_count: Optional[int]
    commission_sum: Optional[int]
    is_decremented: Optional[bool]
    commission_avg: Optional[Decimal]

    # Method fields
    agency: Optional[_AgencyRetrieveModel]
    status: Optional[Any]

    # Totally overrided fields
    checks: Optional[list[_CheckListModel]]

    # Hyperlinks
    hyper_info: Optional[dict[str, Any]]

    @root_validator
    def get_agency(cls, values: dict[str, Any]) -> dict[str, Any]:
        agency: Union[_AgencyRetrieveModel, None] = values.get("agency")
        if agency:
            agency: str = agency.name
        else:
            agency = None
        values["agency"]: Union[str, None] = agency
        return values

    @root_validator
    def get_status(cls, values: dict[str, Any]) -> dict[str, Any]:
        checks: Union[list[Any], None] = values.pop("checks", None)
        if checks:
            check: _CheckListModel = checks[0]
            status: dict[str, Any] = {
                "value": check.unique_status.slug,
                "label": f"{check.unique_status.title} {check.unique_status.subtitle or ''}".strip(),
            }
        else:
            status = None
        values["status"]: Union[dict[str, Any], None] = status
        return values

    @root_validator
    def get_hyper_info(cls, values: dict[str, Any]) -> dict[str, Any]:
        id: int = values.get("id")
        values["hyper_info"]: dict[str, Any] = dict(retrieve=get_hyperlink(f"/users/agents/{id}"))
        return values

    class Config:
        orm_mode = True

        @staticmethod
        def schema_extra(schema: dict[str, Any]) -> None:
            schema["properties"].pop("checks")


class ResponseAgentsUsersListModel(BaseUserModel):
    """
    Модель ответа пользователей агента
    """

    count: int
    page_info: dict[str, Any]
    result: list[_UserListModel]

    class Config:
        orm_mode = True
