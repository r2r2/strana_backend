from typing import Type, Any

from ..entities import BaseAgentCase
from ..models import RequestAcceptContractModel
from ..repos import AgentRepo, User
from src.users.loggers.wrappers import user_changes_logger


class AcceptContractCase(BaseAgentCase):
    """
    Принятие договора
    """

    def __init__(self, agent_repo: Type[AgentRepo]) -> None:
        self.agent_repo: AgentRepo = agent_repo()
        self.agent_update = user_changes_logger(
            self.agent_repo.update, self, content="Принятие договора"
        )

    async def __call__(self, agent_id: int, payload: RequestAcceptContractModel) -> User:
        data: dict[str, Any] = payload.dict()
        filters: dict[str, Any] = dict(id=agent_id)
        agent: User = await self.agent_repo.retrieve(filters=filters)
        await self.agent_update(agent, data=data)
        return agent
