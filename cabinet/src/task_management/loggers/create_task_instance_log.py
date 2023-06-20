from copy import copy
from typing import Any, Optional

from src.task_management.entities import BaseTaskService
from src.task_management.repos import TaskInstanceLogRepo
from src.task_management.types import TaskManagementORM


class CreateTaskInstanceLogLogger(BaseTaskService):
    """
    Создание лога изменения экземпляра задания
    """
    def __init__(
        self,
        task_instance_log_repo: type[TaskInstanceLogRepo],
        orm_class: Optional[type[TaskManagementORM]] = None,
        orm_config: Optional[dict[str, Any]] = None,
    ):
        self.task_instance_log_repo: TaskInstanceLogRepo = task_instance_log_repo()

        self.orm_class: Optional[type[TaskManagementORM]] = orm_class
        self.orm_config: Optional[dict[str, Any]] = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

    async def __call__(self, log_data: dict[str, Any]) -> None:
        await self.task_instance_log_repo.create(data=log_data)
