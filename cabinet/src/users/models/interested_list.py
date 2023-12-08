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


class SlugTypeChoice(StrEnum):
    MINE: str = "mine"
    MANAGER: str = "manager"


class SlugTypeChoiceFilters(CamelCaseBaseModel):
    slug: Optional[SlugTypeChoice]
