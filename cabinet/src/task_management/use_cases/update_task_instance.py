from typing import Any

from src.task_management.exceptions import TaskInstanceNotFoundError
from src.task_management.model import TaskInstanceUpdateSchema
from src.task_management.repos import TaskInstanceRepo, TaskInstance
from src.task_management.services import UpdateTaskInstanceStatusService
from src.task_management.utils import TaskDataBuilder


class UpdateTaskInstanceCase:
    def __init__(
        self,
        task_instance_repo: type[TaskInstanceRepo],
        update_task_service: UpdateTaskInstanceStatusService,
    ):
        self.task_instance_repo: TaskInstanceRepo = task_instance_repo()
        self.update_task_service: UpdateTaskInstanceStatusService = update_task_service

    async def __call__(self, task_instance_id: int, payload: TaskInstanceUpdateSchema) -> dict[str, Any]:
        task_instance: TaskInstance = await self.task_instance_repo.retrieve(
            filters=dict(id=task_instance_id),
            prefetch_fields=["booking__amocrm_status"],
        )
        if not task_instance:
            raise TaskInstanceNotFoundError

        await self.update_task_service(booking_id=task_instance.booking.id, status_slug=payload.slug)

        task: list[dict] = await TaskDataBuilder(
            task_instances=task_instance,
            booking=task_instance.booking,
        ).build()
        if task:
            # В списке будет одна таска
            # Таски может и не быть, если в конкретном статусе букинга она не должна быть видна
            return task[0]
