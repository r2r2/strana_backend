from src.task_management.entities import BaseTaskCase
from src.task_management.exceptions import TaskInstanceNotFoundError
from src.task_management.loggers import task_instance_logger
from src.task_management.repos import TaskInstanceRepo, TaskInstance, TaskStatus


class SetPreviousTaskStatusCase(BaseTaskCase):
    def __init__(
        self,
        task_instance_repo: type[TaskInstanceRepo],
    ):
        self.task_instance_repo = task_instance_repo()

        self.update_task = task_instance_logger(self.task_instance_repo.update, self, content="Обновление задачи")

    async def __call__(self, task_id: int) -> None:
        task: TaskInstance = await self.task_instance_repo.retrieve(
            filters=dict(id=task_id),
            prefetch_fields=["status__tasks_chain__task_statuses"],
        )
        if not task:
            raise TaskInstanceNotFoundError

        task_status: TaskStatus = task.status

        # Задача всегда связана со статусом цепочки задач
        task_chain_statuses: list[TaskStatus] = sorted(
            task.status.tasks_chain.task_statuses,
            key=lambda s: s.priority,
        )

        for idx, status in enumerate(task_chain_statuses):
            # находим нужный статус
            if status.slug == task_status.slug:
                if idx == 0:
                    # если статус первый в цепочке, то ничего не делаем
                    return
                previous_status: TaskStatus = task_chain_statuses[idx - 1]
                await self.update_task(task_instance=task, data=dict(status=previous_status))
                break
