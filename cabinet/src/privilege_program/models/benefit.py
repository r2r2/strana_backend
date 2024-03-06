from typing import Any

from ..entities import BasePrivilegeCamelCaseModel


class PrivilegeBenefitResponse(BasePrivilegeCamelCaseModel):
    """
    Модель ответа для Преимуществ
    """

    slug: str
    title: str
    is_active: bool
    priority: int
    image: dict[str, Any] | None
