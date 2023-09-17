from datetime import datetime
from typing import Optional

from common.pydantic import CamelCaseBaseModel
from src.properties.constants import PropertyStatuses


class ProjectCityResponse(CamelCaseBaseModel):
    slug: str


class ViewedPropertyProjectResponse(CamelCaseBaseModel):
    name: str
    slug: str
    city: ProjectCityResponse

    class Config:
        orm_mode = True


class ViewedPropertyFloorResponse(CamelCaseBaseModel):
    number: str


class ViewedPropertyBuildingResponse(CamelCaseBaseModel):
    name: str
    total_floor: Optional[int]


class ViewedPropertyFeatureResponse(CamelCaseBaseModel):
    name: str
    description: str


class ViewedPropertyResponse(CamelCaseBaseModel):
    """
    Модель ответа добавленного объекта недвижимости
    """
    id: int
    client_id: int
    property_id: int
    updated_at: datetime
    created_at: datetime


class ViewedPropertyListResponse(CamelCaseBaseModel):
    """
    Модель ответа добавленного объекта недвижимости
    """
    id: int
    plan: Optional[dict]
    project: Optional[ViewedPropertyProjectResponse]
    rooms: Optional[int]
    area: Optional[float]
    status: PropertyStatuses.serializer
    floor: Optional[ViewedPropertyFloorResponse]
    total_floors: Optional[int]
    building: Optional[ViewedPropertyBuildingResponse]
    price: Optional[int]
    number: Optional[str]
    special_offers: Optional[str]
    features: Optional[list[ViewedPropertyFeatureResponse]]

    class Config:
        orm_mode = True
