from typing import Any

from src.task_management.entities import BaseTaskService
from src.task_management.repos import TaskInstanceLogRepo


class CreateTaskInstanceLogLogger(BaseTaskService):
    """
    Создание лога изменения экземпляра задания
    """
    def __init__(
        self,
        task_instance_log_repo: type[TaskInstanceLogRepo],
    ):
        self.task_instance_log_repo: TaskInstanceLogRepo = task_instance_log_repo()

    async def __call__(self, *, log_data: dict[str, Any]) -> None:
        await self.task_instance_log_repo.create(data=log_data)
