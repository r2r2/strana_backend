import asyncio
from datetime import datetime
from typing import Any

from pytz import UTC

from src.users.entities import BaseUserCase
from src.users.exceptions import UserNotFoundError, ConfirmClientAssignNotFoundError
from src.users.repos import UserRepo, User, ConfirmClientAssignRepo, ConfirmClientAssign


class ConfirmAssignClientCase(BaseUserCase):
    """
    Кейс подтверждения закрепления клиента
    """
    def __init__(
        self,
        user_repo: type[UserRepo],
        confirm_client_assign_repo: type[ConfirmClientAssignRepo],
    ):
        self.user_repo = user_repo()
        self.confirm_client_assign_repo = confirm_client_assign_repo()

    async def __call__(self, user_id: int) -> None:
        client: User = await self.user_repo.retrieve(
            filters=dict(id=user_id),
            related_fields=["agent", "agency"]
        )
        if not client:
            raise UserNotFoundError

        confirm_client: ConfirmClientAssign = await self.confirm_client_assign_repo.retrieve(
            filters=dict(client=client, agent=client.agent, agency=client.agency)
        )
        if not confirm_client:
            raise ConfirmClientAssignNotFoundError

        data: dict[str, Any] = dict(
            assign_confirmed_at=datetime.now(tz=UTC),
        )
        asyncio.create_task(self.confirm_client_assign_repo.update(confirm_client, data=data))
