from typing import Any

from src.task_management.entities import BaseTaskCase
from src.task_management.exceptions import TaskInstanceNotFoundError
from src.task_management.repos import TaskInstanceRepo, TaskInstance
from src.task_management.utils import TaskDataBuilder


class GetTaskInstanceCase(BaseTaskCase):
    def __init__(
        self,
        task_instance_repo: type[TaskInstanceRepo],
    ):
        self.task_instance_repo: TaskInstanceRepo = task_instance_repo()

    async def __call__(self, task_id: int) -> dict[str, Any]:
        task: TaskInstance = await self.task_instance_repo.retrieve(
            filters=dict(id=task_id),
            prefetch_fields=["booking__amocrm_status"],
        )
        if not task:
            raise TaskInstanceNotFoundError

        tasks: list[dict] = await TaskDataBuilder(
            task_instances=task,
            booking=task.booking,
        ).build()
        if tasks:
            # В списке будет одна таска
            # Таски может и не быть, если в конкретном статусе букинга она не должна быть видна
            return tasks[0]
