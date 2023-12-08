import binascii
from decimal import Decimal
from typing import Any, Optional
from pydantic import root_validator, Field

from common.utils import from_global_id
from common.pydantic import CamelCaseBaseModel
from src.properties.constants import PropertyTypes
from src.properties.entities import BasePropertyModel


class PropertyFloorModel(BasePropertyModel):
    """
    Модель этажа интересующего объекта пользователя
    """

    id: Optional[int]
    number: Optional[str]

    class Config:
        orm_mode = True


class PropertyTypeModel(CamelCaseBaseModel):
    """
    Модель типа бронирования в базе.
    """

    slug: Optional[str]
    label: Optional[str]

    class Config:
        orm_mode = True


class PropertySectionModel(CamelCaseBaseModel):
    """
    Модель типа секции в базе.
    """

    id: Optional[int]
    name: Optional[str]
    total_floors: Optional[int]
    number: Optional[str]

    class Config:
        orm_mode = True


class PropertyRetrieveModel(BasePropertyModel):
    """
    Модель объекта недвижимости
    """

    id: int
    price: Optional[int]
    rooms: Optional[int]
    number: Optional[str]
    article: Optional[str]
    area: Optional[Decimal]
    discount: Optional[int]
    global_id: Optional[str]
    backend_id: Optional[int]
    original_price: Optional[int]
    final_price: Optional[int]
    plan: Optional[dict[str, Any]]
    plan_png: Optional[dict[str, Any]]
    floor: Optional[PropertyFloorModel]
    type: PropertyTypes.serializer | None
    property_type: Optional[PropertyTypeModel] = Field(None, alias="propertyType")
    section: Optional[PropertySectionModel]

    @root_validator
    def decode_backend_id(cls, values: dict) -> dict:
        """Parse backend property_id from global_id"""

        try:
            _, values['backend_id'] = from_global_id(values.get('global_id'))
        except (binascii.Error, AttributeError):
            pass
        return values

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
