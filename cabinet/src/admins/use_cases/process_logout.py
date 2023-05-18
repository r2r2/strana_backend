from typing import Any

from ..types import AdminSession
from ..entities import BaseAdminCase


class ProcessLogoutCase(BaseAdminCase):
    """
    Процессинг выхода
    """

    def __init__(self, session: AdminSession, session_config: dict[str, Any]) -> None:
        self.session: AdminSession = session
        self.auth_key: str = session_config["auth_key"]

    async def __call__(self) -> None:
        self.session[self.auth_key]: dict[str, None] = dict(type=None, token=None)
        await self.session.insert()
