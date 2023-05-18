from typing import Any

from ..types import UserSession
from ..entities import BaseUserCase


class SessionTokenCase(BaseUserCase):
    """
    Получение токена через сессию
    """

    def __init__(self, session: UserSession, session_config: dict[str, str]) -> None:
        self.session: UserSession = session
        self.auth_key: str = session_config["auth_key"]

    async def __call__(self) -> dict[str, Any]:
        return await self.session.get(self.auth_key, dict(type=None, token=None))
