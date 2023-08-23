from typing import Optional

from pydantic import root_validator
from src.projects.constants import ProjectSkyColor

from ..constants import BuildingType
from ..entities import BaseBuildingCamelCaseBaseModel


class FloorResponse(BaseBuildingCamelCaseBaseModel):
    """
    Модель ответа этажа
    """
    id: int
    number: int
    commercial_count: int
    flats_count: int

    class Config:
        orm_mode = True


class BuildingSectionResponse(BaseBuildingCamelCaseBaseModel):
    """
    Модель ответа секции корпуса из портала
    """
    id: int
    name: Optional[str]
    number: Optional[str]
    flats_count: Optional[int]
    total_floors: Optional[int]
    floor_set: list[FloorResponse]

    class Config:
        orm_mode = True


class BuildingProjectResponse(BaseBuildingCamelCaseBaseModel):
    """
    Модель ответа проекта для корпуса
    """
    name: str
    card_image: Optional[dict]
    card_image_display: Optional[dict]
    card_image_night: Optional[dict]
    card_image_night_display: Optional[dict]
    card_sky_color: ProjectSkyColor.serializer
    project_color: str
    discount: int

    @root_validator
    def set_image_displays(cls, values: dict) -> dict:
        if values.get("card_image"):
            values["card_image_display"] = values["card_image"]
        if values.get("card_image_night"):
            values["card_image_night_display"] = values["card_image_night"]
        return values


class BuildingDetailResponse(BaseBuildingCamelCaseBaseModel):
    """
    Модель ответа корпуса из портала
    """
    id: int
    name: str
    global_id: str
    name_display: Optional[str]
    address: str
    project: BuildingProjectResponse
    kind: Optional[BuildingType.serializer]
    flats_count: int
    total_floor: Optional[int]
    parking_count: Optional[int]
    commercial_count: int
    built_year: Optional[int]
    ready_quarter: Optional[int]
    flats_0_min_price: Optional[int]
    flats_1_min_price: Optional[int]
    flats_2_min_price: Optional[int]
    flats_3_min_price: Optional[int]
    flats_4_min_price: Optional[int]
    section_set: list[BuildingSectionResponse]
    discount: int

    @root_validator
    def validate_discount(cls, values: dict) -> dict:
        if not values.get("discount"):
            discount: int = values.get("project").discount
            values["discount"] = discount
        return values

    class Config:
        orm_mode = True
