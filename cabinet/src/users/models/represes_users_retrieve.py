from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Union, Any
from pydantic import root_validator as method_field

from src.booking import constants as booking_constants
from src.properties.constants import PropertyTypes

from ..constants import UserStatus
from ..entities import BaseUserModel


class RequestRepresesUsersRetrieveModel(BaseUserModel):
    """
    Модель запроса детального пользователя представителя агенства
    """

    class Config:
        orm_mode = True


class _InterestedFloorListModel(BaseUserModel):
    """
    Модель этажа интересующего объекта пользователя
    """

    id: int
    number: Optional[str]

    class Config:
        orm_mode = True


class _InterestedProjectListModel(BaseUserModel):
    """
    Модель проекта интересующего объекта пользователя
    """

    id: int
    slug: Optional[str]
    name: Optional[str]

    class Config:
        orm_mode = True


class _InterestedPropertyListModel(BaseUserModel):
    """
    Модель объекта интересующего объекта пользователя
    """

    id: int
    plan: Optional[dict[str, Any]]
    price: Optional[int]
    rooms: Optional[int]
    number: Optional[str]
    article: Optional[str]
    area: Optional[Decimal]
    plan_png: Optional[dict[str, Any]]
    original_price: Optional[int]
    type: Optional[PropertyTypes.serializer]

    class Config:
        orm_mode = True


class _InterestedBuildingListModel(BaseUserModel):
    """
    Модель корпуса интересующего объекта пользователя
    """

    id: int
    name: Optional[str]

    class Config:
        orm_mode = True


class _IndentFloorListModel(BaseUserModel):
    """
    Модель этажа забронированного объекта пользователя
    """

    id: int
    number: Optional[str]

    class Config:
        orm_mode = True


class _IndentProjectListModel(BaseUserModel):
    """
    Модель проекта забронированного объекта пользователя
    """

    id: int
    slug: Optional[str]
    name: Optional[str]
    city: Optional[str]

    class Config:
        orm_mode = True


class _IndentPropertyListModel(BaseUserModel):
    """
    Модель объекта забронированного объекта пользователя
    """

    id: int
    plan: Optional[dict[str, Any]]
    price: Optional[int]
    rooms: Optional[int]
    number: Optional[str]
    article: Optional[str]
    area: Optional[Decimal]
    plan_png: Optional[dict[str, Any]]
    original_price: Optional[int]
    type: Optional[PropertyTypes.serializer]

    class Config:
        orm_mode = True


class _IndentBuildingListModel(BaseUserModel):
    """
    Модель корпуса забронированного объекта пользователя
    """

    id: int
    name: Optional[str]

    class Config:
        orm_mode = True


class _InterestedListModel(BaseUserModel):
    """
    Модель интересующего объекта пользователя
    """

    floor: Optional[_InterestedFloorListModel]
    project: Optional[_InterestedProjectListModel]
    property: Optional[_InterestedPropertyListModel]
    building: Optional[_InterestedBuildingListModel]

    class Config:
        orm_mode = True


class _IndentListModel(BaseUserModel):
    """
    Модель бронирования пользователя
    """

    id: int
    decremented: bool
    until: Optional[datetime]
    expires: Optional[datetime]
    commission: Optional[Decimal]
    decrement_reason: Optional[str]
    commission_value: Optional[Decimal]
    amocrm_stage: Optional[booking_constants.BookingStages.serializer]
    amocrm_substage: Optional[booking_constants.BookingSubstages.serializer]

    floor: Optional[_IndentFloorListModel]
    project: Optional[_IndentProjectListModel]
    property: Optional[_IndentPropertyListModel]
    building: Optional[_IndentBuildingListModel]

    class Config:
        orm_mode = True


class _AgentRetrieveModel(BaseUserModel):
    """
    Модель агента пользователя представителя агенства
    """

    id: Optional[int]
    name: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]

    class Config:
        orm_mode = True


class _CheckRetrieveModel(BaseUserModel):
    """
    Модель проверки пользователя агента
    """

    status: Optional[UserStatus.serializer]

    class Config:
        orm_mode = True


class ResponseRepresesUsersRetrieveModel(BaseUserModel):
    """
    Модель ответа детального пользователя представителя агенства
    """

    id: int
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    surname: Optional[str]
    work_end: Optional[date]
    patronymic: Optional[str]
    work_start: Optional[date]
    agent: Optional[_AgentRetrieveModel]
    indents: Optional[list[_IndentListModel]]
    interesting: Optional[list[_InterestedListModel]]

    # Totally overrided fields
    checks: Optional[list[_CheckRetrieveModel]]

    # Method fields
    status: Optional[UserStatus.serializer]

    @method_field
    def get_status(cls, values: dict[str, Any]) -> dict[str, Any]:
        checks: Union[list[Any], None] = values.pop("checks", None)
        if checks:
            status: dict[str, Any] = checks[0].status.dict()
        else:
            status = None
        values["status"]: Union[dict[str, Any], None] = status
        return values

    class Config:
        orm_mode = True

        @staticmethod
        def schema_extra(schema: dict[str, Any]) -> None:
            schema["properties"].pop("checks")
