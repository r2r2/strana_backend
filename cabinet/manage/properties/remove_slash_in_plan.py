from copy import copy
from typing import Any

import structlog
from tortoise import Tortoise, BaseDBAsyncClient
from tortoise import connections

from config import tortoise_config


class RemoveSlashInPlan:
    def __init__(self):
        self.logger = structlog.get_logger(self.__class__.__name__)
        self.orm_class: type[Tortoise] = Tortoise
        self.orm_config: dict[str, Any] = copy(tortoise_config)
        self.orm_config.pop("generate_schemas", None)

    def __await__(self):
        return self().__await__()

    async def __call__(self, *args):
        self.logger.info("Запущен скрипт для удаления слешей в планах")
        await self.orm_class.init(config=self.orm_config)
        query: str = """
            UPDATE properties_property
            SET plan = OVERLAY(plan PLACING '' FROM 1 FOR POSITION('/' IN plan))
            WHERE POSITION('/' IN plan) = 1;
        """
        conn: BaseDBAsyncClient = connections.get("cabinet")
        await conn.execute_script(query)
        await self.orm_class.close_connections()
        self.logger.info("Завершен скрипт для удаления слешей в планах")
