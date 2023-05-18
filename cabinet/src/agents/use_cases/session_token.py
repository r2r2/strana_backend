from typing import Any

from ..types import AgentSession
from ..entities import BaseAgentCase


class SessionTokenCase(BaseAgentCase):
    """
    Получение токена через сессию
    """

    def __init__(self, session: AgentSession, session_config: dict[str, str]) -> None:
        self.session: AgentSession = session
        self.auth_key: str = session_config["auth_key"]

    async def __call__(self) -> dict[str, Any]:
        return await self.session.get(self.auth_key, dict(type=None, token=None, role=None))
