from typing import Optional

from pydantic import BaseModel, NoneStr

from src.agencies.constants import AgencyType


class AgencyBaseModel(BaseModel):
    id: int
    name: NoneStr
    inn: Optional[str]
    city: Optional[str]
    type: Optional[AgencyType.serializer]

    class Config:
        orm_mode = True


class AgencyRetrieveModel(AgencyBaseModel):
    pass
