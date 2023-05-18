from typing import Any

from ..types import AdminSession
from ..entities import BaseAdminCase


class SessionTokenCase(BaseAdminCase):
    """
    Получение токена через сессию
    """

    def __init__(self, session: AdminSession, session_config: dict[str, str]) -> None:
        self.session: AdminSession = session
        self.auth_key: str = session_config["auth_key"]

    async def __call__(self) -> dict[str, Any]:
        return await self.session.get(self.auth_key, dict(type=None, token=None, role=None))
