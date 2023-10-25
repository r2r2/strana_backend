import asyncio
from typing import Type

from common.amocrm import AmoCRM
from src.agents.entities import BaseAgentCase
from src.agents.exceptions import AgentNotFoundError
from src.agents.models import UpdateProfileModel
from src.agents.repos import AgentRepo, User
from src.users.loggers.wrappers import user_changes_logger


class UpdateProfileCase(BaseAgentCase):
    """ Изменение персональных данных агента"""

    def __init__(
            self,
            agent_repo: Type[AgentRepo],
            amocrm_class: Type[AmoCRM],
            user_type: str,
    ) -> None:
        self.agent_repo: AgentRepo = agent_repo()
        self.agent_update = user_changes_logger(
            self.agent_repo.update, self, content="Обновление профиля агента"
        )
        self.user_type = user_type
        self.amocrm_class = amocrm_class

    async def __call__(self, agent_id: int, payload: UpdateProfileModel) -> User:
        filters = dict(id=agent_id, type=self.user_type)
        agent: User = await self.agent_repo.retrieve(filters=filters)
        if not agent:
            raise AgentNotFoundError
        data = payload.dict()

        await asyncio.gather(
            self.agent_update(agent, data=data),
            self._update_amo_info(agent, payload)
        )

        agent: User = await self.agent_repo.retrieve(filters=filters, related_fields=["agency", "agency__general_type"])

        return agent

    async def _update_amo_info(self, agent: User, payload: UpdateProfileModel) -> None:
        """Invoke amo API"""
        # In AMO we have only one field for full name,
        # there is no separate field for patronymic
        async with await self.amocrm_class() as amocrm:
            await amocrm.update_contact(
                user_id=agent.amocrm_id,
                user_name=self._get_fullname(agent, payload)
            )

    @staticmethod
    def _get_fullname(agent: User, payload: UpdateProfileModel) -> str:
        name = payload.name or agent.name or ""
        surname = payload.surname or agent.surname or ""
        patronymic = payload.patronymic or agent.patronymic or ""
        return f"{surname} {name} {patronymic}"
