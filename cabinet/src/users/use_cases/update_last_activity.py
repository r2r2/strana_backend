import time
from typing import Any

from src.users.entities import BaseUserCase
from src.users.types import UserSession


class UpdateLastActivityCase(BaseUserCase):
    """
    Обновление времени последней активности пользователя
    """

    def __init__(self, session: UserSession, session_config: dict[str, Any]) -> None:
        self.session: UserSession = session
        self.last_activity_key: str = session_config["last_activity_key"]

    async def __call__(self) -> None:
        await self.session.set(self.last_activity_key, int(time.time()))
