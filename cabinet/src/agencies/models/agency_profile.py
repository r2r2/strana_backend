from typing import Optional

from common import wrappers
from common.files.models import FileCategoryListModel
from src.agencies.constants import AgencyType
from src.agencies.entities import BaseAgencyModel


class ResponseGetAgencyProfile(BaseAgencyModel):
    name: Optional[str]
    inn: Optional[str]
    city: Optional[str]
    type: Optional[AgencyType.serializer]
    files: Optional[list[FileCategoryListModel]]

    class Config:
        orm_mode = True


@wrappers.as_form
class RequestUpdateProfile(BaseAgencyModel):
    name: Optional[str]
