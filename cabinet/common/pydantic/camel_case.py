from pydantic import BaseModel

from common.utils import to_camel_case


class CamelCaseBaseModel(BaseModel):
    class Config:
        alias_generator = to_camel_case
        allow_population_by_field_name = True
