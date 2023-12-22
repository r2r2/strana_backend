from enum import StrEnum
from typing import Any, Optional

from common.pydantic import CamelCaseBaseModel


class ResponseInterestsList(CamelCaseBaseModel):
    """
    Модель ответа со списком global_id объектов
    """
    count: int
    page_info: dict[str, Any]
    result: list[str]

    class Config:
        orm_mode = True


class PropertyData(CamelCaseBaseModel, frozen=True):
    profitbase_id: int
    global_id: str


class ResponseInterestsListProfitId(CamelCaseBaseModel):
    """
    Модель ответа со списком profitbase_id объектов
    """
    count: int
    page_info: dict[str, Any]
    result: list[PropertyData]

    class Config:
        orm_mode = True


class SlugTypeChoice(StrEnum):
    MINE: str = "mine"
    MANAGER: str = "manager"


class SlugTypeChoiceFilters(CamelCaseBaseModel):
    slug: Optional[SlugTypeChoice]
