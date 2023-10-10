from pydantic import Field

from ..entities import BaseUserModel


class ConsultationType(BaseUserModel):
    name: str = Field(alias='text')
    slug: str

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
