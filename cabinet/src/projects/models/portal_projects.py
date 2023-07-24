from typing import Optional

from ..entities import BaseProjectCamelCaseBaseModel
from ..constants import ProjectStatus, ProjectSkyColor


class ProjectCityResponse(BaseProjectCamelCaseBaseModel):
    """
    Модель ответа транспорта для ЖК
    """
    id: int
    name: str
    short_name: Optional[str]
    color: Optional[str]


class ProjectTransportResponse(BaseProjectCamelCaseBaseModel):
    """
    Модель ответа города для ЖК
    """
    id: Optional[int]
    name: Optional[str]
    icon_content: Optional[str]


class ProjectMetroResponse(BaseProjectCamelCaseBaseModel):
    """
    Модель ответа города для ЖК
    """
    name: Optional[str]


class ProjectDetailResponse(BaseProjectCamelCaseBaseModel):
    """
    Модель ответа ЖК из портала
    """
    id: int
    name: str
    slug: str
    title: Optional[str]
    status: Optional[ProjectStatus.serializer]
    global_id: str
    transport: Optional[ProjectTransportResponse]
    transport_time: Optional[int]
    metro: Optional[ProjectMetroResponse]
    flats_count: int
    commercial_count: int
    parking_pantry_count: int
    min_flat_price: Optional[int]
    flat_area_range: dict[str, Optional[float]]
    city: Optional[ProjectCityResponse]
    card_image: Optional[dict]
    card_image_display: Optional[dict]
    card_image_night: Optional[dict]
    card_image_night_display: Optional[dict]
    card_sky_color: ProjectSkyColor.serializer
    project_color: str

    class Config:
        orm_mode = True
