from typing import Any

from ..types import RepresSession
from ..entities import BaseRepresCase


class SessionTokenCase(BaseRepresCase):
    """
    Получение токена через сессию
    """

    def __init__(self, session: RepresSession, session_config: dict[str, str]) -> None:
        self.session: RepresSession = session
        self.auth_key: str = session_config["auth_key"]

    async def __call__(self) -> dict[str, Any]:
        return await self.session.get(self.auth_key, dict(type=None, token=None, role=None))
