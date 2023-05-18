from re import match
from typing import Any, Type

from ..entities import BaseAgencyCase
from ..repos import AgencyRepo, Agency


class AdminsAgenciesLookupCase(BaseAgencyCase):
    """
    Поиск агенства администратором
    """

    phone_regex: str = r"^[0-9\s]{1,20}$"

    def __init__(self, search_types: Any, agency_repo: Type[AgencyRepo]) -> None:
        self.agency_repo: AgencyRepo = agency_repo()
        self.search_types: Any = search_types

    async def __call__(self, lookup: str, init_filters: dict[str, Any]) -> dict[str, Any]:
        contained_plus: bool = "+" in lookup
        lookup: str = lookup.replace("+", "").replace("-", "").replace("(", "").replace(")", "")
        if match(self.phone_regex, lookup) or contained_plus:
            lookup_type: str = self.search_types.PHONE
        elif lookup.isascii() and lookup:
            lookup_type: str = self.search_types.EMAIL
        else:
            lookup_type: str = self.search_types.NAME
        search: list[list[dict[str, Any]]] = init_filters.pop("search", list())
        init_filters.pop("ordering", None)
        filters: dict[str, Any] = dict(is_deleted=False)
        filters.update(init_filters)
        if len(search) == 1:
            q_filters: list[Any] = [self.agency_repo.q_builder(or_filters=search[0])]
        else:
            q_base: Any = self.agency_repo.q_builder()
            for s in search:
                q_base |= self.agency_repo.q_builder(and_filters=s)
            q_filters: list[Any] = [q_base]
        agencies: list[Agency] = await self.agency_repo.list(filters=filters, q_filters=q_filters)
        data: dict[str, Any] = dict(type=self.search_types(value=lookup_type), result=agencies)
        return data
