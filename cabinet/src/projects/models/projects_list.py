from typing import Optional, Any
from pydantic import Field, root_validator

from ..entities import BaseProjectModel
from ..constants import ProjectStatus


class RequestProjectsListModel(BaseProjectModel):
    """
    Модель запроса списка проектов
    """

    class Config:
        orm_mode = True


class ProjectListModel(BaseProjectModel):
    """
    Модель проекта в списке
    """
    id: int
    global_id: Optional[str]
    slug: Optional[str]
    name: Optional[str]
    city: Optional[Any]
    city_name: Optional[str]
    status: Optional[ProjectStatus.serializer]

    @root_validator
    def validate_city(cls, values: dict[str, Any]) -> dict[str, Any]:
        city = values.pop('city', None)
        values['city'] = city.slug if city else None
        values['city_name'] = city.name if city else None
        return values

    class Config:
        orm_mode = True


class ResponseProjectsListModel(BaseProjectModel):
    """
    Модель ответа списка проектов
    """
    count: int
    page_info: dict[str, Any]
    result: list[ProjectListModel]

    class Config:
        orm_mode = True


class ResponseAdditionalProjectsListModel(BaseProjectModel):
    """
    Модель ответа списка проектов (для api v2)
    """
    id: int
    slug: Optional[str]
    name: Optional[str]
    city: Optional[Any]
    status: Optional[ProjectStatus.serializer]
    has_additional_templates: bool = Field(alias="hasAdditionalTemplates")

    @root_validator
    def validate_city(cls, values: dict[str, Any]) -> dict[str, Any]:
        city = values.pop('city', None)
        values['city'] = city.slug if city else None
        return values

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
