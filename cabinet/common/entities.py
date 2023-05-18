from typing import Type, Any

from pydantic import BaseModel

from common.orm.entities import BaseRepo


class BaseFilter(BaseModel):
    """
    Базовый фильтр
    """
    class Filter:
        repo: Type[BaseRepo]
        exclude: list[str]
        choices: list[str]
        additions: dict[str, Any]
        labels: dict[str, Any]
        specs_overrides: dict[str, Any]
        facets_overrides: dict[str, Any]

    class Credentials:
        options: dict[str, Any]

    class Order:
        fields: dict[str, Any]
