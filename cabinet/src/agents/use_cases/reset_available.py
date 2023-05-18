from pytz import UTC
from datetime import datetime
from typing import Any, Union, Type

from ..repos import AgentRepo, User
from ..types import AgentSession
from ..entities import BaseAgentCase


class ResetAvailableCase(BaseAgentCase):
    """
    Доступность сброса пароля
    """

    def __init__(
        self,
        user_type: str,
        session: AgentSession,
        agent_repo: Type[AgentRepo],
        session_config: dict[str, Any],
    ) -> None:
        self.agent_repo: AgentRepo = agent_repo()

        self.user_type: str = user_type
        self.session: AgentSession = session
        self.password_reset_key: str = session_config["password_reset_key"]

    async def __call__(self) -> dict[str, bool]:
        agent_id: Union[int, None] = await self.session.get(self.password_reset_key)
        filters: dict[str, Any] = dict(
            id=agent_id, type=self.user_type, is_active=True, is_approved=True
        )
        agent: User = await self.agent_repo.retrieve(filters=filters)
        available: bool = bool(
            agent
            and agent.reset_time
            and not agent.discard_token
            and agent.reset_time > datetime.now(tz=UTC)
        )
        data: dict[str, Any] = dict(available=available)
        return data
