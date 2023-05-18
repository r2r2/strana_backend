from src.users.entities import BaseUserCase
from src.users.exceptions import UserNotFoundError
from src.users.models import ConfirmClientAssign
from src.users.repos import UserRepo, User


class ConfirmAssignClientCase(BaseUserCase):
    """
    Кейс подтверждения закрепления клиента
    """
    def __init__(
        self,
        user_repo: type[UserRepo],
    ):
        self.user_repo = user_repo()

    async def __call__(self, payload: ConfirmClientAssign, user_id: int) -> None:
        user: User = await self.user_repo.retrieve(filters=dict(id=user_id))
        if not user:
            raise UserNotFoundError
        await self.user_repo.update(user, data=dict(is_assigned=payload.is_assigned))
