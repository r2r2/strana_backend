from src.task_management.entities import BaseTaskCase
from src.task_management.exceptions import TaskInstanceNotFoundError
from src.task_management.repos import (
    TaskGroupStatus,
    TaskGroupStatusRepo,
    TaskChain,
    TaskInstanceRepo,
    TaskInstance,
)


class TaskChainStatusesCase(BaseTaskCase):
    """
    Получение групповых статусов цепочки заданий
    """
    def __init__(
        self,
        task_group_status_repo: type[TaskGroupStatusRepo],
        task_instance_repo: type[TaskInstanceRepo],
    ):
        self.task_group_status_repo: TaskGroupStatusRepo = task_group_status_repo()
        self.task_instance_repo: TaskInstanceRepo = task_instance_repo()

    async def __call__(self, task_id: int) -> list[TaskGroupStatus]:
        task: TaskInstance = await self.task_instance_repo.retrieve(
            filters=dict(id=task_id),
            related_fields=["status__tasks_chain"],
        )
        if not task:
            raise TaskInstanceNotFoundError

        task_chain: TaskChain = task.status.tasks_chain
        group_statuses: list[TaskGroupStatus] = await self.task_group_status_repo.list(
            filters=dict(task_chain=task_chain),
            related_fields=["task_chain"],
            prefetch_fields=["statuses"],
        ).order_by("priority")
        return group_statuses
