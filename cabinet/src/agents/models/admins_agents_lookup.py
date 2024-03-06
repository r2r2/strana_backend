from typing import Optional, Any
from pydantic import root_validator as method_field
from src.users import constants as users_constants

from ..entities import BaseAgentModel


class RequestAdminsAgentsLookupModel(BaseAgentModel):
    """
    Модель запроса поиска агента администратором
    """

    class Config:
        orm_mode = True


class _AgentListModel(BaseAgentModel):
    """
    Модель агента представителя агенства
    """

    id: int
    email: Optional[str]
    phone: Optional[str]
    is_approved: bool

    # Method fields
    fio: Optional[str]

    # Totally overrided fields
    name: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]

    @method_field
    def get_fio(cls, values: dict[str, Any]) -> dict[str, Any]:
        name: str = values.pop("name").capitalize() if values.get("name") else str()
        surname: str = values.pop("surname").capitalize() if values.get("surname") else str()
        patronymic: str = values.pop("patronymic").capitalize() if values.get("patronymic") else str()
        fio: str = f"{surname} {name} {patronymic}"
        if not patronymic:
            fio: str = f"{surname} {name}"
        values["fio"]: str = fio
        return values

    class Config:
        orm_mode = True

        @staticmethod
        def schema_extra(schema: dict[str, Any]) -> None:
            schema["properties"].pop("name")
            schema["properties"].pop("surname")
            schema["properties"].pop("patronymic")


class ResponseAdminsAgentsLookupModel(BaseAgentModel):
    """
    Модель ответа поиска агента администратором
    """

    type: Optional[users_constants.SearchType.serializer]
    result: Optional[list[_AgentListModel]]

    class Config:
        orm_mode = True
