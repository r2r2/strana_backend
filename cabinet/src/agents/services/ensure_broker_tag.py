from typing import Type, Optional

from common.amocrm import AmoCRM
from ..repos import AgentRepo, User
from ..entities import BaseAgentService
from src.users.loggers.wrappers import user_changes_logger


class EnsureBrokerTagService(BaseAgentService):
    """
    Назначение тега 'Риелтор' контакту в AmoCRM.
    """

    def __init__(self, agent_repo: Type[AgentRepo], amocrm_class: Type[AmoCRM]) -> None:
        self.agent_repo: AgentRepo = agent_repo()
        self.agent_update = user_changes_logger(
            self.agent_repo.update, self, content="Назначение тега 'Риелтор' контакту в AmoCRM"
        )

        self.amocrm_class: Type[AmoCRM] = amocrm_class

    async def __call__(self, agent: Optional[User] = None) -> None:
        agent_tags: Optional[list[str]] = agent.tags
        if agent_tags is None:
            agent_tags = []

        if self.amocrm_class.broker_tag not in agent_tags:
            agent_tags.append(self.amocrm_class.broker_tag)
            async with await self.amocrm_class() as amocrm:
                await amocrm.update_contact(user_id=agent.amocrm_id, user_tags=agent_tags)
            await self.agent_update(agent, data=dict(tags=agent_tags))
