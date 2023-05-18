from pytz import UTC
from datetime import datetime
from typing import Type, Any, Callable, Union

from src.admins.repos import AdminRepo
from src.agents.repos import AgentRepo
from src.represes.repos import RepresRepo
from src.users.loggers.wrappers import user_changes_logger
from ..repos import User
from ..entities import BaseUserCase
from ..types import UserSession, UserHasher
from ..models import RequestChangePasswordModel
from ..exceptions import UserChangePasswordError, UserSamePasswordError, UserPasswordTimeoutError


class ChangePasswordCase(BaseUserCase):
    """
    Смена пароля
    """

    def __init__(
        self,
        user_type: str,
        session: UserSession,
        user_repo: Union[Type[AgentRepo], Type[AdminRepo], Type[RepresRepo]],
        session_config: dict[str, Any],
        hasher: Callable[..., UserHasher],
    ) -> None:
        self.hasher: UserHasher = hasher()
        self.user_repo: Union[AgentRepo, AdminRepo, RepresRepo] = user_repo()
        self.user_update = user_changes_logger(
            self.user_repo.update, self, content="Смена пароля пользователя"
        )

        self.user_type: str = user_type
        self.session: UserSession = session

        self.password_reset_key: str = session_config["password_reset_key"]

    async def __call__(
        self, user_id: Union[int, None], payload: RequestChangePasswordModel
    ) -> User:
        data: dict[str, Any] = payload.dict()
        password: str = data["password"]
        from_session: bool = False
        if not user_id:
            user_id: int = await self.session.get(self.password_reset_key)
            from_session: bool = True
            if not user_id:
                raise UserChangePasswordError
        filters: dict[str, Any] = dict(id=user_id, type=self.user_type, is_approved=True)
        user: User = await self.user_repo.retrieve(filters=filters)
        if not user:
            raise UserChangePasswordError
        if self.hasher.verify(password, user.password):
            raise UserSamePasswordError
        if from_session and (not user.reset_time or user.reset_time < datetime.now(tz=UTC)):
            raise UserPasswordTimeoutError
        data: dict[str, Any] = dict(password=self.hasher.hash(password), reset_time=None)
        await self.user_update(user, data=data)
        await self.session.pop(self.password_reset_key)
        return user
