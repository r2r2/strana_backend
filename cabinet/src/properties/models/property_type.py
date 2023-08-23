from common.pydantic import CamelCaseBaseModel
from pydantic import Field


class ResponsePropertyTypeModel(CamelCaseBaseModel):
    """
    Модель типов объектов недвижимости.
    """

    slug: str = Field(alias="value")
    label: str

    class Config:
        allow_population_by_field_name = True
