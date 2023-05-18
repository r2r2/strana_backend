from typing import Any, Type

from ..repos import User, AgentRepo
from ..entities import BaseAgentCase
from ..exceptions import AgentNotFoundError


class GetMeCase(BaseAgentCase):
    """
    Получение текущего агента
    """

    def __init__(self, agent_repo: Type[AgentRepo]) -> None:
        self.agent_repo: AgentRepo = agent_repo()

    async def __call__(self, agent_id: int) -> User:
        filters: dict[str, Any] = dict(id=agent_id)
        agent: User = await self.agent_repo.retrieve(filters=filters, related_fields=["agency"])
        if not agent:
            raise AgentNotFoundError
        return agent
