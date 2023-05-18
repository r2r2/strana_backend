from copy import copy
from typing import Any, Optional, Type, Union

from ..repos import UserLogRepo
from ..entities import BaseUserService
from ..types import UserORM


class CreateUserLogger(BaseUserService):
    """
    Создание лога пользователя
    """

    def __init__(
        self,
        user_log_repo: Type[UserLogRepo],
        orm_class: Optional[Type[UserORM]] = None,
        orm_config: Optional[dict[str, Any]] = None,
    ) -> None:
        self.user_log_repo: UserLogRepo = user_log_repo()

        self.orm_class: Union[Type[UserORM], None] = orm_class
        self.orm_config: Union[dict[str, Any], None] = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

    async def __call__(self, log_data: dict[str, Any]) -> None:
        await self.user_log_repo.create(data=log_data)
