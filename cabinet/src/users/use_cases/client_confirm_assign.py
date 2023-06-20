import asyncio
from datetime import datetime
from typing import Any

from pytz import UTC

from src.users.entities import BaseUserCase
from src.users.exceptions import ConfirmClientAssignNotFoundError
from src.users.repos import ConfirmClientAssignRepo, ConfirmClientAssign
from src.users.services import GetAgentClientFromQueryService


class ConfirmAssignClientCase(BaseUserCase):
    """
    Кейс подтверждения закрепления клиента
    """
    def __init__(
        self,
        get_agent_client_service: GetAgentClientFromQueryService,
        confirm_client_assign_repo: type[ConfirmClientAssignRepo],
    ):
        self.get_agent_client_service: GetAgentClientFromQueryService = get_agent_client_service
        self.confirm_client_assign_repo = confirm_client_assign_repo()

    async def __call__(self, token: str, data: str) -> None:
        agent, client = await self.get_agent_client_service(token=token, data=data)

        confirm_client: ConfirmClientAssign = await self.confirm_client_assign_repo.retrieve(
            filters=dict(client=client, agent=agent, agency=agent.agency)
        )
        if not confirm_client:
            raise ConfirmClientAssignNotFoundError

        data: dict[str, Any] = dict(
            assign_confirmed_at=datetime.now(tz=UTC),
        )
        asyncio.create_task(self.confirm_client_assign_repo.update(confirm_client, data=data))
