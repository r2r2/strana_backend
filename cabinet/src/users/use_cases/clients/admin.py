from re import match
from typing import Any, Callable, Coroutine, Type

from ...constants import SearchType, UserType
from ...entities import BaseUserCase
from ...repos import User, UserRepo

__all__ = ('AdminClientsSpecsCase', 'AdminClientsFacetsCase', 'AdminClientsLookupCase')


class AdminClientsSpecsCase(BaseUserCase):
    """
    Спеки пользователей администратором
    """

    group: str = "agent_id"

    async def __call__(self, specs: Callable[..., Coroutine]) -> dict[str, Any]:
        filters: dict[str, Any] = dict(type=UserType.CLIENT)
        result: dict[str, Any] = await specs(group=self.group, filters=filters)
        return result


class AdminClientsFacetsCase(BaseUserCase):
    """
    Фасеты пользователей администратором
    """

    group: str = "agent_id"

    def __init__(self, user_repo: Type[UserRepo]) -> None:
        self.user_repo: UserRepo = user_repo()

    async def __call__(
        self, init_filters: dict[str, Any], facets: Callable[..., Coroutine]
    ) -> dict[str, Any]:
        filters: dict[str, Any] = dict(type=UserType.CLIENT)
        search: list[list[dict[str, Any]]] = init_filters.pop("search", [])
        filters.update(init_filters)
        if len(search) == 1:
            q_filters: list[Any] = [self.user_repo.q_builder(or_filters=search[0])]
        else:
            q_base: Any = self.user_repo.q_builder()
            for s in search:
                q_base |= self.user_repo.q_builder(and_filters=s)
            q_filters: list[Any] = [q_base]
        result: dict[str, Any] = await facets(
            group=self.group, filters=filters, q_filters=q_filters
        )
        return result


class AdminClientsLookupCase(BaseUserCase):
    """
    Поиск пользователя администратором
    """

    phone_regex: str = r"^[0-9\s]{1,20}$"

    def __init__(self, user_repo: Type[UserRepo]) -> None:
        self.user_repo: UserRepo = user_repo()

    async def __call__(self, lookup: str, init_filters: dict[str, Any]) -> dict[str, Any]:
        contained_plus: bool = "+" in lookup
        lookup: str = lookup.replace("+", "").replace("-", "").replace("(", "").replace(")", "")
        if match(self.phone_regex, lookup) or contained_plus:
            lookup_type: str = SearchType.PHONE
        elif lookup.isascii() and lookup:
            lookup_type: str = SearchType.EMAIL
        else:
            lookup_type: str = SearchType.NAME
        search: list[list[dict[str, Any]]] = init_filters.pop("search", [])
        init_filters.pop("ordering", None)
        filters: dict[str, Any] = dict(type=UserType.CLIENT)
        filters.update(init_filters)
        if len(search) == 1:
            q_filters: list[Any] = [self.user_repo.q_builder(or_filters=search[0])]
        else:
            q_base: Any = self.user_repo.q_builder()
            for s in search:
                q_base |= self.user_repo.q_builder(and_filters=s)
            q_filters: list[Any] = [q_base]
        users: list[User] = await self.user_repo.list(filters=filters, q_filters=q_filters)
        data: dict[str, Any] = dict(type=SearchType(value=lookup_type), result=users)
        return data
