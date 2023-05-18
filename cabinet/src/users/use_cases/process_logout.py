from typing import Any

from fastapi import Response

from ..types import UserSession
from ..entities import BaseUserCase


class ProcessLogoutCase(BaseUserCase):
    """
    Процессинг выхода
    """

    def __init__(
        self,
        session: UserSession,
        session_config: dict[str, Any],
        response: Response,
    ) -> None:
        self.session: UserSession = session
        self.auth_key: str = session_config["auth_key"]
        self.key: str = session_config["key"]
        self.domain: str = session_config["domain"]
        self.response: Response = response

    async def __call__(self) -> None:
        self.session[self.auth_key]: dict[str, None] = dict(type=None, token=None)
        await self.session.insert()
        await self.session.redis.delete(self.session.session_id)
        self.response.delete_cookie(key=self.key, domain=self.domain)

