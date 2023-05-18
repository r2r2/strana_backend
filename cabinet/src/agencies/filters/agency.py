from re import match
from typing import Any, Optional, Type

from common.wrappers import filterize
from pydantic import Field
from pydantic import root_validator as field_overrider

from ..entities import BaseAgencyFilter
from ..repos import AgencyRepo


@filterize
class AgencyFilter(BaseAgencyFilter):
    """
    Фильтр агенств
    """

    search: Optional[str] = Field(alias="search", description="Поиск")
    ordering: Optional[str] = Field(alias="ordering", description="Сортировка")

    @field_overrider
    def override_search(cls, values: dict[str, Any]) -> dict[str, Any]:
        """override search"""
        phone_regex: str = r"^[0-9\s]{1,20}$"
        if search := values.get("search"):
            contained_plus: bool = "+" in search
            search: str = search.replace("+", "").replace("-", "").replace("(", "").replace(")", "")
            if match(phone_regex, search) or contained_plus:
                search: str = search.replace(" ", "").replace("_", "")
                values["search"]: list[list[dict[str, Any]]] = [
                    [dict(maintainer__phone__icontains=search)]
                ]
            elif search.isascii():
                values["search"]: list[list[dict[str, Any]]] = [
                    [dict(maintainer__email__icontains=search)]
                ]
            else:
                values["search"]: list[list[dict[str, Any]]] = [
                    [dict(name__icontains=search)]
                ]
        return values

    class Order:
        fields: dict[str, Any] = {
            "name": "по {type} имени"
        }

    class Filter:
        repo: Type[AgencyRepo] = AgencyRepo
        exclude: list[str] = ["search", "ordering"]
