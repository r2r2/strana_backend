from typing import Optional, Any, Union
from pydantic import root_validator
from src.users import constants as users_constants
from ..entities import BaseAgentModel


class RequestRepresesAgentsRetrieveModel(BaseAgentModel):
    """
    Модель запроса детального агента представителя агенства
    """

    class Config:
        orm_mode = True


class _CheckListModel(BaseAgentModel):
    """
    Модель проверки пользователя в списке
    """

    unique_status: Optional[Any]

    class Config:
        orm_mode = True


class _UserListModel(BaseAgentModel):
    """
    Модель пользователя в списке
    """

    id: int
    name: Optional[str]
    phone: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]

    # Method fields
    status: Optional[Any]

    # Totally overrided fields
    checks: Optional[list[_CheckListModel]]

    @root_validator
    def get_status(cls, values: dict[str, Any]) -> dict[str, Any]:
        checks: Union[list[_CheckListModel], None] = values.pop("checks")
        result: Any = None
        if checks:
            for check in checks:
                unique_status = check.unique_status
                result: dict[str, Any] = {
                    "value": check.unique_status.slug if check.unique_status else None,
                    "label": f"{check.unique_status.title} {check.unique_status.subtitle or ''}".strip(),
                }
                if unique_status.slug == users_constants.UserStatus.UNIQUE:
                    break
        values["status"]: dict[str, Any] = result
        return values

    class Config:
        orm_mode = True

        @staticmethod
        def schema_extra(schema: dict[str, Any]) -> None:
            schema["properties"].pop("checks")


class ResponseRepresesAgentsRetrieveModel(BaseAgentModel):
    """
    Модель ответа детального агента представителя агенства
    """

    id: int
    is_approved: bool
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]
    closed_clients: Optional[int]
    active_clients: Optional[int]
    succeeded_clients: Optional[int]
    type: Optional[users_constants.UserType.serializer]

    clients: Optional[list[_UserListModel]]

    class Config:
        orm_mode = True
