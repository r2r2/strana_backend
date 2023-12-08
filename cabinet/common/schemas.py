from typing import Any

from pydantic import BaseModel


class UrlEncodeDTO(BaseModel):
    """
    Схема для url encode

    @params: host - хост
    @params: route_template - шаблон для route
    @params: route_params - параметры пути, которые нужно вставить
    @params: query_params - query параметры запроса
    """
    host: str
    route_template: str
    route_params: list[str, Any] | None
    query_params: dict[str, Any] | None
    use_ampersand_ascii: bool = False
