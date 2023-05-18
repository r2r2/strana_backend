from typing import Optional, Any
from pydantic import root_validator as method_field
from pydantic import Field

from ..constants import SearchType
from ..entities import BaseUserModel


class RequestAdminsUsersLookupModel(BaseUserModel):
    """
    Модель запроса поиска пользователя в списке бронирований
    """

    class Config:
        orm_mode = True


class _BookingListModel(BaseUserModel):
    """
    Модель пользователя агента
    """

    user__id: int = Field(alias="id")
    user__email: Optional[str] = Field(alias="email")
    user__phone: Optional[str] = Field(alias="phone")

    # Method fields
    fio: Optional[str]

    # Totally overrided fields
    user__name: Optional[str]
    user__surname: Optional[str]
    user__patronymic: Optional[str]

    @method_field
    def get_fio(cls, values: dict[str, Any]) -> dict[str, Any]:
        name: Any = values.pop("user__name", str())
        name: str = (name if name else str()).capitalize()
        surname: Any = values.pop("user__surname", str())
        surname: str = (surname if surname else str()).capitalize()
        patronymic: Any = values.pop("user__patronymic", str())
        patronymic: str = (patronymic if patronymic else str()).capitalize()
        fio: str = f"{surname} {name} {patronymic}"
        if not patronymic:
            fio: str = f"{surname} {name}"
        values["fio"]: str = fio
        return values

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

        @staticmethod
        def schema_extra(schema: dict[str, Any]) -> None:
            schema["properties"].pop("user__name")
            schema["properties"].pop("user__surname")
            schema["properties"].pop("user__patronymic")


class ResponseBookingUsersLookupModel(BaseUserModel):
    """
    Модель ответа поиска пользователя в списке бронирований
    """

    type: Optional[SearchType.serializer]
    result: Optional[list[_BookingListModel]]

    class Config:
        orm_mode = True
