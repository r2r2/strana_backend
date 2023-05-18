from pydantic import Field
from typing import Optional, Any, Type

from common.wrappers import filterize

from ..repos import ManagersRepo
from ..entities import BaseManagerFilter


async def city_facets(
        group: str, queryset: Any, repo: ManagersRepo, addition: dict[str, Any]) -> dict[str, Any]:
    """
    Фасеты фильтра города
    """
    facets: list[Any] = await repo.cities_facets(queryset=queryset)
    if not facets:
        facets: list[dict[str, Any]] = list()
    return facets


@filterize
class ManagerFilter(BaseManagerFilter):
    """
    Фильтр менеджера
    """

    ordering: Optional[str] = Field(alias="ordering", description="Сортировка")
    city__in: Optional[list] = Field(alias="city", description="Фильтр по городу")

    class Filter:
        repo: Type[ManagersRepo] = ManagersRepo

        exclude: list[str] = ["ordering"]
        choices: list[str] = ["city"]

        facets_overrides: dict[str, Any] = {"city": city_facets}
