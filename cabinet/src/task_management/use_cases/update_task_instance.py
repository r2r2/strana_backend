from typing import Type

from src.task_management.exceptions import TaskInstanceNotFoundError, TaskStatusNotFoundError
from src.task_management.model import TaskInstanceUpdateSchema
from src.task_management.repos import TaskInstanceRepo, TaskInstance, TaskStatusRepo, TaskStatus


class UpdateTaskInstanceCase:
    def __init__(
            self,
            task_instance_repo: Type[TaskInstanceRepo],
            task_status_repo: Type[TaskStatusRepo],
    ):
        self.task_instance_repo: TaskInstanceRepo = task_instance_repo()
        self.task_status_repo: TaskStatusRepo = task_status_repo()

    async def __call__(self, task_instance_id: int, payload: TaskInstanceUpdateSchema) -> TaskInstance:
        task_instance: TaskInstance = await self.task_instance_repo.retrieve(filters=dict(id=task_instance_id))
        if not task_instance:
            raise TaskInstanceNotFoundError

        task_status: TaskStatus = await self.task_status_repo.retrieve(filters=dict(slug=payload.slug))
        if not task_status:
            raise TaskStatusNotFoundError
        return await self.task_instance_repo.update(model=task_instance, data=dict(status=task_status))

