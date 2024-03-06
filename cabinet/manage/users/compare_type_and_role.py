from copy import copy
from typing import Any

import structlog
from tortoise import Tortoise, connections, BaseDBAsyncClient

from config import tortoise_config


class CompareTypeAndRole:
    """
    Проверка работы сервиса рассылки уведомлений для избранного клиентов.
    """

    def __init__(self) -> None:
        self.orm_class: type[Tortoise] = Tortoise
        self.orm_config: dict[str, Any] = copy(tortoise_config)
        self.orm_config.pop("generate_schemas", None)

        self.logger: structlog.BoundLogger = structlog.get_logger(__name__)

    async def __call__(self, *args, **kwargs) -> None:
        self.logger.info("Запущен скрипт для сопоставления тип/роль и роли")
        await self.orm_class.init(config=self.orm_config)
        query: str = """
            UPDATE users_user
            SET role_id = (SELECT id FROM users_roles WHERE users_roles.slug = users_user.type)
            WHERE users_user.type != (SELECT slug FROM users_roles WHERE users_roles.id = users_user.role_id) OR users_user.role_id IS NULL;
        """
        conn: BaseDBAsyncClient = connections.get("cabinet")
        await conn.execute_script(query)
        await self.orm_class.close_connections()
        self.logger.info("Завершен скрипт для сопоставления тип/роль и роли")
