from typing import Optional

from pydantic import BaseModel, NoneStr, validator

from src.agencies.constants import AgencyType


class AgencyBaseModel(BaseModel):
    id: int
    name: NoneStr
    inn: Optional[str]
    city: Optional[str]
    type: Optional[AgencyType.serializer]

    @validator("city", pre=True)
    def get_city_name(cls, value):
        if value:
            return value.name
        return None

    class Config:
        orm_mode = True


class AgencyRetrieveModel(AgencyBaseModel):
    pass
