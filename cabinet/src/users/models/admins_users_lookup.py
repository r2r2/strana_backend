from typing import Optional, Any
from pydantic import root_validator as method_field

from ..constants import SearchType
from ..entities import BaseUserModel


class RequestAdminsUsersLookupModel(BaseUserModel):
    """
    Модель запроса поиска пользователя администратором
    """

    class Config:
        orm_mode = True


class _UserListModel(BaseUserModel):
    """
    Модель пользователя агента
    """

    id: int
    email: Optional[str]
    phone: Optional[str]

    # Method fields
    fio: Optional[str]

    # Totally overrided fields
    name: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]

    @method_field
    def get_fio(cls, values: dict[str, Any]) -> dict[str, Any]:
        name: Any = values.pop("name", str())
        name: str = (name if name else str()).capitalize()
        surname: Any = values.pop("surname", str())
        surname: str = (surname if surname else str()).capitalize()
        patronymic: Any = values.pop("patronymic", str())
        patronymic: str = (patronymic if patronymic else str()).capitalize()
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


class ResponseAdminsUsersLookupModel(BaseUserModel):
    """
    Модель ответа поиска пользователя администратором
    """

    type: Optional[SearchType.serializer]
    result: Optional[list[_UserListModel]]

    class Config:
        orm_mode = True
