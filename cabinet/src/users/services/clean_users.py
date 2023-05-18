from copy import copy
from typing import Type

import structlog
from tortoise import Tortoise

from ..entities import BaseUserService
from ..constants import UserType
from ..repos import User, UserRepo


class CleanUsersService(BaseUserService):
    """
    Периодическая очистка пользователей
    """

    def __init__(
            self,
            user_repo: Type[UserRepo],
            orm_class: Type[Tortoise],
            orm_config: dict,
    ) -> None:
        self.user_repo: UserRepo = user_repo()
        self.logger = structlog.getLogger(__name__)
        self.orm_class = orm_class
        self.orm_config = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

    async def __call__(self):
        clean_filters: dict = dict(type=UserType.CLIENT, amocrm_id=None, bookings=None)
        users: list[User] = await self.user_repo.list(filters=clean_filters)

        if users:
            for user in users:
                await self.user_repo.delete(model=user)

        self.logger.info(f"Deleted users: {users}")
