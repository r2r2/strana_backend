# pylint: disable=no-self-argument

from typing import Any, Optional, Union

from pydantic import NoneStr, validator
from pydantic import root_validator as method_field

from src.agencies.constants import AgencyType
from ..entities import BaseAgencyModel


class _MaintainerRetrieveModel(BaseAgencyModel):
    """
    Модель детального администратора
    """

    name: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]

    class Config:
        orm_mode = True


class _AgencyListModel(BaseAgencyModel):
    """
    Модель агенства в списке
    """

    id: int
    is_approved: bool
    name: Optional[str]
    active_agents: Optional[int]
    active_clients: Optional[int]
    inn: NoneStr
    amocrm_id: Optional[int]
    city: NoneStr
    type: AgencyType.serializer

    # Method fields
    admin: Optional[str]
    phone: Optional[str]
    email: Optional[str]

    # Totally overrided fields
    maintainer: Optional[_MaintainerRetrieveModel]

    @method_field
    def get_maintainer_info(cls, values: dict[str, Any]) -> dict[str, Any]:
        """
        Получение информации представителя агенства
        """
        maintainer: Union[_MaintainerRetrieveModel, None] = values.pop("maintainer", None)
        if maintainer:
            values["admin"]: str = (
                f"{maintainer.surname + ' ' if maintainer.surname else str()}"
                f"{maintainer.name[0].capitalize() + '.' if maintainer.name else str()}"
                f"{maintainer.patronymic[0].capitalize() + '.' if maintainer.patronymic else str()}"
            )
            values["phone"]: str = maintainer.phone
            values["email"]: str = maintainer.email
        else:
            values["admin"] = None
            values["phone"] = None
            values["email"] = None
        return values

    @validator("city", pre=True)
    def get_city_name(cls, value):
        if value:
            return value.name
        return None

    class Config:
        orm_mode = True

        @staticmethod
        def schema_extra(schema: dict[str, Any]) -> None:
            schema["properties"].pop("maintainer")


class ResponseAdminsAgenciesListModel(BaseAgencyModel):
    """
    Модель ответа списка агенств администратором
    """

    count: int
    page_info: dict[str, Any]
    result: list[_AgencyListModel]

    class Config:
        orm_mode = True
