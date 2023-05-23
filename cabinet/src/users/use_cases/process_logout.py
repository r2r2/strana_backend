from typing import Any

from fastapi import Response, Request

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
        request: Request,
    ) -> None:
        self.session: UserSession = session
        self.auth_key: str = session_config["auth_key"]
        self.key: str = session_config["key"]
        self.response: Response = response
        self.request: Request = request

    async def __call__(self) -> None:
        self.session[self.auth_key]: dict[str, None] = dict(type=None, token=None)
        await self.session.insert()
        await self.session.redis.delete(self.session.session_id)
        for cookie in self.request.cookies:
            self.response.delete_cookie(key=cookie)
