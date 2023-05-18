from typing import Any, Optional, Type

import structlog
from common.amocrm import AmoCRM
from common.amocrm.types import AmoContact

from ..entities import BaseUserService
from ..exceptions import UserNotFoundError
from ..repos import User, UserRepo


class UpdateUsersService(BaseUserService):
    """
    Импорт(обновление) данных пользователей из AmoCRM
    """

    def __init__(
            self,
            amocrm_class: Type[AmoCRM],
            user_repo: Type[UserRepo],
    ) -> None:
        self.user_repo: UserRepo = user_repo()
        self.amocrm_class: Type[AmoCRM] = amocrm_class
        self.logger = structlog.getLogger(__name__)

    async def __call__(self, user_id: int):
        user: User = await self.user_repo.retrieve(filters=dict(id=user_id))
        if not user:
            raise UserNotFoundError

        async with await self.amocrm_class() as amocrm:
            contact: Optional[AmoContact] = await amocrm.fetch_contact(user_id=user.amocrm_id)
            if not contact:
                self.logger.warning("User has not found at amo contact")
                return

            data: dict[str, Any] = dict(
                name=contact.first_name,
                surname=contact.last_name,
                # is_deleted=contact.is_deleted  временное решения для фикса
            )

            await self.user_repo.update(model=user, data=data)
