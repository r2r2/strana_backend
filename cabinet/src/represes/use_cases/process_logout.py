from typing import Any

from ..types import RepresSession
from ..entities import BaseRepresCase


class ProcessLogoutCase(BaseRepresCase):
    """
    Процессинг выхода
    """

    def __init__(self, session: RepresSession, session_config: dict[str, Any]) -> None:
        self.session: RepresSession = session
        self.auth_key: str = session_config["auth_key"]

    async def __call__(self) -> None:
        self.session[self.auth_key]: dict[str, None] = dict(type=None, token=None)
        await self.session.insert()
