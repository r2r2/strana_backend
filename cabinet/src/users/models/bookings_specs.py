from typing import Any, Optional
from pydantic import Field

from ..entities import BaseUserModel


class _ResponseBookingSpecsModelProject(BaseUserModel):
    """
    Модель пользователя спек бронирований для проектов.
    """

    project__slug: Optional[str] = Field(alias="value")
    project__name: Optional[str] = Field(alias="label")

    class Config:
        allow_population_by_field_name = True


class _ResponseBookingSpecsModelAgent(BaseUserModel):
    """
    Модель пользователя спек бронирований для агентов.
    """

    agent__id: Optional[int] = Field(alias="value")
    agent__surname: Optional[str] = Field(alias="label")

    class Config:
        allow_population_by_field_name = True


class _ResponseBookingSpecsModel(BaseUserModel):
    """
    Модель ответа спек бронирований.
    """

    agent: Optional[list[_ResponseBookingSpecsModelAgent]]
    status: Optional[list[Any]]
    project: Optional[list[_ResponseBookingSpecsModelProject]]
    property: Optional[list[Any]]


class ResponseBookingSpecs(BaseUserModel):
    """
    Модель ответа спек бронирований с сортировкой.
    """

    specs: Optional[_ResponseBookingSpecsModel]
    ordering: list[Any]
