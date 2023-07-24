from typing import Optional, Any

from pydantic import validator

from common import wrappers
from common.files.models import FileCategoryListModel
from src.agencies.constants import AgencyType
from src.agencies.entities import BaseAgencyModel


class ResponseGetAgencyProfile(BaseAgencyModel):
    name: Optional[str]
    inn: Optional[str]
    city: Optional[Any]
    type: Optional[AgencyType.serializer]
    files: Optional[list[FileCategoryListModel]]

    @validator("city", pre=True)
    def get_city_name(cls, value):
        if value:
            return value.name
        return None

    class Config:
        orm_mode = True


@wrappers.as_form
class RequestUpdateProfile(BaseAgencyModel):
    name: Optional[str]
