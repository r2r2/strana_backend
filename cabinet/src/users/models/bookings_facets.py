from typing import Optional, Any

from ..entities import BaseUserModel


class _ResponseBookingFacetsModel(BaseUserModel):
    """
    Модель пользователя фасет бронирований.
    """

    agent: Optional[list[int]]
    status: Optional[list[Any]]
    project: Optional[list[str]]
    property: Optional[list[str]]


class ResponseBookingFacets(BaseUserModel):
    """
    Модель ответа фасет бронирований с сортировкой.
    """

    facets: Optional[_ResponseBookingFacetsModel]
