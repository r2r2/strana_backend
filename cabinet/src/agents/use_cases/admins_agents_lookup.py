from re import match
from typing import Type, Any

from ..entities import BaseAgentCase
from ..repos import AgentRepo, User


class AdminsAgentsLookupCase(BaseAgentCase):
    """
    Поиск агента администратором
    """

    phone_regex: str = r"^[0-9\s]{1,20}$"

    def __init__(self, user_type: str, agent_repo: Type[AgentRepo], search_types: Any) -> None:
        self.agent_repo: AgentRepo = agent_repo()

        self.user_type: str = user_type
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
        filters: dict[str, Any] = dict(type=self.user_type, is_deleted=False)
        filters.update(init_filters)
        if len(search) == 1:
            q_filters: list[Any] = [self.agent_repo.q_builder(or_filters=search[0])]
        else:
            q_base: Any = self.agent_repo.q_builder()
            for s in search:
                q_base |= self.agent_repo.q_builder(and_filters=s)
            q_filters: list[Any] = [q_base]
        agents: list[User] = await self.agent_repo.list(filters=filters, q_filters=q_filters)
        data: dict[str, Any] = dict(type=self.search_types(value=lookup_type), result=agents)
        return data
