from typing import Any, Optional
from pydantic import Field

from ..entities import BaseUserModel


class _ResponseClientSpecsModelProject(BaseUserModel):
    """
    Модель пользователя спек клиентов для проектов.
    """

    bookings__project__slug: Optional[str] = Field(alias="value")
    bookings__project__name: Optional[str] = Field(alias="label")

    class Config:
        allow_population_by_field_name = True


class _ResponseClientSpecsModelAgent(BaseUserModel):
    """
    Модель пользователя спек клиентов для агентов.
    """

    agent__id: Optional[int] = Field(alias="value")
    agent__name: Optional[str] = Field(alias="label")

    class Config:
        allow_population_by_field_name = True


class _ResponseClientSpecsModel(BaseUserModel):
    """
    Модель ответа спек клиентов.
    """

    agent: Optional[list[_ResponseClientSpecsModelAgent]]
    project: Optional[list[_ResponseClientSpecsModelProject]]


class ResponseClientSpecs(BaseUserModel):
    """
    Модель ответа спек клиентов с сортировкой.
    """

    specs: Optional[_ResponseClientSpecsModel]
    ordering: list[Any]
