from typing import Any

from .programs import PrivilegeProgramListResponse
from ..entities import BasePrivilegeCamelCaseModel


class ProgramByCategoryResponse(BasePrivilegeCamelCaseModel):
    """
    Модель ответа категорий
    """

    slug: str
    title: str
    display_type: str
    image: dict[str, Any] | None
    results: list[PrivilegeProgramListResponse] | None

    class Config:
        orm_mode = True
