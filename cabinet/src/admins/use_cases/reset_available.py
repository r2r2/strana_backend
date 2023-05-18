from pytz import UTC
from datetime import datetime
from typing import Any, Union, Type

from ..repos import AdminRepo, User
from ..types import AdminSession
from ..entities import BaseAdminCase


class ResetAvailableCase(BaseAdminCase):
    """
    Доступность сброса пароля
    """

    def __init__(
        self,
        user_type: str,
        session: AdminSession,
        admin_repo: Type[AdminRepo],
        session_config: dict[str, Any],
    ) -> None:
        self.admin_repo: AdminRepo = admin_repo()

        self.user_type: str = user_type
        self.session: AdminSession = session
        self.password_reset_key: str = session_config["password_reset_key"]

    async def __call__(self) -> dict[str, bool]:
        admin: Union[int, None] = await self.session.get(self.password_reset_key)
        filters: dict[str, Any] = dict(
            id=admin, type=self.user_type, is_active=True, is_approved=True
        )
        admin: User = await self.admin_repo.retrieve(filters=filters)
        available: bool = bool(
            admin
            and admin.reset_time
            and not admin.discard_token
            and admin.reset_time > datetime.now(tz=UTC)
        )
        data: dict[str, Any] = dict(available=available)
        return data
