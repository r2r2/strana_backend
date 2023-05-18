from pytz import UTC
from datetime import datetime
from typing import Any, Union, Type

from ..repos import RepresRepo, User
from ..types import RepresSession
from ..entities import BaseRepresCase


class ResetAvailableCase(BaseRepresCase):
    """
    Доступность сброса пароля
    """

    def __init__(
        self,
        user_type: str,
        session: RepresSession,
        repres_repo: Type[RepresRepo],
        session_config: dict[str, Any],
    ) -> None:
        self.repres_repo: RepresRepo = repres_repo()

        self.user_type: str = user_type
        self.session: RepresSession = session
        self.password_reset_key: str = session_config["password_reset_key"]

    async def __call__(self) -> dict[str, bool]:
        repres_id: Union[int, None] = await self.session.get(self.password_reset_key)
        filters: dict[str, Any] = dict(
            id=repres_id, type=self.user_type, is_active=True, is_approved=True
        )
        repres: User = await self.repres_repo.retrieve(filters=filters)
        available: bool = bool(
            repres
            and repres.reset_time
            and not repres.discard_token
            and repres.reset_time > datetime.now(tz=UTC)
        )
        data: dict[str, Any] = dict(available=available)
        return data
