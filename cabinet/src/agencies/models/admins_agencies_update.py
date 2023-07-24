from typing import Optional

from common import wrappers
from common.files.models import FileCategoryListModel
from pydantic import NoneStr, constr, validator

from ..constants import AgencyType
from ..entities import BaseAgencyModel


@wrappers.as_form
class RequestAdminsAgenciesUpdateModel(BaseAgencyModel):
    """
    Модель запроса изменения агенства администратором
    """

    inn: NoneStr
    city: NoneStr
    name: Optional[constr(max_length=50)]

    class Config:
        orm_mode = True


class ResponseAdminsAgenciesUpdateModel(BaseAgencyModel):
    """
    Модель ответа изменения агенства администратором
    """

    id: int
    name: str
    inn: Optional[str]
    city: Optional[str]
    type: Optional[AgencyType.serializer]
    files: Optional[list[FileCategoryListModel]]

    @validator("city", pre=True)
    def get_city_name(cls, value):
        if value:
            return value.name
        return None

    class Config:
        orm_mode = True
