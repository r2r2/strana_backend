from typing import Any

from ..types import AgentSession
from ..entities import BaseAgentCase


class ProcessLogoutCase(BaseAgentCase):
    """
    Процессинг выхода
    """

    def __init__(self, session: AgentSession, session_config: dict[str, Any]) -> None:
        self.session: AgentSession = session
        self.auth_key: str = session_config["auth_key"]

    async def __call__(self) -> None:
        self.session[self.auth_key]: dict[str, None] = dict(type=None, token=None)
        await self.session.insert()
