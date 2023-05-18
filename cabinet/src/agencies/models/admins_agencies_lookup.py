from typing import Optional, Any, Union

from pydantic import root_validator as method_field, NoneStr
from src.users import constants as users_constants

from ..entities import BaseAgencyModel


class RequestAdminsAgenciesLookupModel(BaseAgencyModel):
    """
    Модель запроса поиска агенства администратором
    """

    class Config:
        orm_mode = True


class _MaintainerRetrieveModel(BaseAgencyModel):
    """
    Модель детального администратора
    """

    phone: Optional[str]
    email: Optional[str]

    class Config:
        orm_mode = True


class _AgencyListModel(BaseAgencyModel):
    """
    Модель агенства в списке
    """

    id: int
    name: Optional[str]
    inn: NoneStr
    city: NoneStr

    # Method fields
    email: Optional[str]
    phone: Optional[str]

    # Totally overrided fields
    maintainer: Optional[_MaintainerRetrieveModel]

    @method_field
    def get_maintainer_data(cls, values: dict[str, Any]) -> dict[str, Any]:
        maintainer: Union[_MaintainerRetrieveModel, None] = values.pop("maintainer", None)
        if maintainer:
            values["phone"]: str = maintainer.phone
            values["email"]: str = maintainer.email
        else:
            values["phone"] = None
            values["email"] = None
        return values

    class Config:
        orm_mode = True

        @staticmethod
        def schema_extra(schema: dict[str, Any]) -> None:
            schema["properties"].pop("maintainer")


class ResponseAdminsAgenciesLookupModel(BaseAgencyModel):
    """
    Модель ответа поиска агенства администратором
    """

    type: Optional[users_constants.SearchType.serializer]
    result: Optional[list[_AgencyListModel]]

    class Config:
        orm_mode = True
