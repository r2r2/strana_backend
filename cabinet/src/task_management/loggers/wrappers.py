from typing import Optional, Any

from common.loggers.utils import get_difference_between_two_dicts
from src.task_management.entities import BaseTaskService
from src.task_management.repos import TaskInstanceRepo, TaskInstance


def task_instance_logger(task_change: TaskInstanceRepo(), service: BaseTaskService, content: str):
    from src.task_management.tasks import create_task_instance_log_task
    """
    Логирование изменений экземпляра задания
    """
    async def _wrapper(task_instance: TaskInstance = None, data: dict = None, filters: dict = None):
        task_instance_after, response_data = dict(), dict()
        task_instance_before: dict[str, Any] = dict(task_instance) if task_instance else dict()
        task_instance_difference: dict[str, Any] = dict()
        error_data = task_instance_id = None

        if data and filters:
            update_task_instance = task_change(filters=filters, data=data)
        elif task_instance and data:
            update_task_instance = task_change(model=task_instance, data=data)
        elif task_instance:
            update_task_instance = task_change(model=task_instance)
        else:
            update_task_instance = task_change(data=data)

        try:
            task_instance: TaskInstance = await update_task_instance
            task_instance_id: Optional[int] = task_instance.id if task_instance else None
            task_instance_after: dict[str, Any] = dict(task_instance) if task_instance else dict()
            task_instance_difference: dict[str, Any] = get_difference_between_two_dicts(
                task_instance_before, task_instance_after
            )

        except Exception as error:
            error_data = str(error)

        log_data: dict[str, Any] = dict(
            state_before=task_instance_before,
            state_after=task_instance_after,
            state_difference=task_instance_difference,
            content=content,
            task_instance_id=task_instance_id,
            response_data=response_data,
            use_case=service.__class__.__name__,
            error_data=error_data,
        )
        create_task_instance_log_task.delay(log_data=log_data)

        return task_instance

    return _wrapper
