from typing import Optional

from ..entities import BaseUserModel


class _ResponseClientFacetsModel(BaseUserModel):
    """
    Модель пользователя фасет клиентов.
    """

    agent: Optional[list[int]]
    project: Optional[list[str]]


class ResponseClientFacets(BaseUserModel):
    """
    Модель ответа фасет клиентов с сортировкой.
    """

    facets: Optional[_ResponseClientFacetsModel]
