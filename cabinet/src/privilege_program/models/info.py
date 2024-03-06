from typing import Any

from ..entities import BasePrivilegeCamelCaseModel


class PrivilegeInfoResponse(BasePrivilegeCamelCaseModel):
    """
    Модель ответа для Основной информации
    """

    slug: str
    title: str
    description: str
    image: dict[str, Any] | None
