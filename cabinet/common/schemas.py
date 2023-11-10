from typing import Any

from pydantic import BaseModel


class UrlEncodeDTO(BaseModel):
    """
    Схема для url encode

    @params: url_template - шаблон url
    @params: host - хост
    @params: query_params - query параметры запроса
    """
    url_template: str
    host: str
    query_params: dict[str, Any] | None
