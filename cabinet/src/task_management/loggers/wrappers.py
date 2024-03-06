import asyncio
from datetime import datetime
from typing import Any, Coroutine

from common.loggers.utils import get_difference_between_two_dicts
from src.task_management.entities import BaseTaskService, BaseTaskCase
from src.task_management.repos import TaskInstanceRepo, TaskInstance, TaskInstanceLogRepo
from src.task_management import loggers


def task_instance_logger(task_change: TaskInstanceRepo(), service: BaseTaskService | BaseTaskCase, content: str):
    async def _wrapper(task_instance: TaskInstance = None, data: dict = None, filters: dict = None):
        task_instance_before = dict(task_instance) if isinstance(task_instance, TaskInstance) else dict()
        context = content
        new_status = data.get("status") if data else None

        if data and filters:
            task_instance = await update_task_instance(task_change(filters=filters, data=data))

        elif task_instance and data:
            context += f": {task_instance.status.name} >> {new_status.name if new_status else ''}"
            task_instance = await update_task_instance(task_change(model=task_instance, data=data))

        elif task_instance:
            task_instance = await update_task_instance(task_change(model=task_instance))

        else:
            context += f": {new_status.name if new_status else ''}"
            task_instance = await update_task_instance(task_change(data=data))

        task_instance_after = dict(task_instance) if task_instance else dict()
        error_data = task_instance if isinstance(task_instance, str) else None

        if task_instance:
            await task_instance.fetch_related("booking", "status__tasks_chain")

        await log_task_instance_change(
            task_instance,
            task_instance_before,
            task_instance_after,
            context,
            service,
            error_data,
        )

        return task_instance

    return _wrapper


async def update_task_instance(task_instance: Coroutine) -> TaskInstance | str:
    try:
        return await task_instance
    except Exception as error:
        return str(error)


async def log_task_instance_change(
    task_instance: TaskInstance | None,
    task_instance_before: dict[str, Any],
    task_instance_after: dict[str, Any],
    content: str,
    service: BaseTaskService | BaseTaskCase,
    error_data: str | None,
) -> None:
    task_instance_id = task_instance.id if task_instance else None
    booking_id = task_instance.booking.id if task_instance else None
    task_chain_id = task_instance.status.tasks_chain.id if task_instance else None
    task_instance_difference = get_difference_between_two_dicts(task_instance_before, task_instance_after)
    serialize_datetime(task_instance_before, task_instance_after, task_instance_difference)

    log_data: dict[str, Any] = dict(
        state_before=task_instance_before,
        state_after=task_instance_after,
        state_difference=task_instance_difference,
        content=content,
        task_instance_id=task_instance_id,
        use_case=service.__class__.__name__,
        error_data=error_data,
        booking_id=booking_id,
        task_chain_id=task_chain_id,
    )
    _: asyncio.Task = asyncio.create_task(
        create_task_instance_log(log_data=log_data),
    )


def serialize_datetime(
    before: dict[str, Any],
    after: dict[str, Any],
    difference: dict[str, Any],
) -> None:
    if before:
        serialize_datetime_fields(before)

    if after:
        serialize_datetime_fields(after)

    if difference:
        serialize_datetime_fields(difference)


def serialize_datetime_fields(
    data: dict[str, Any],
) -> None:
    datetime_format: str = "%d.%m.%Y %H:%M:%S"

    for field, value in data.items():
        if isinstance(value, datetime):
            data[field] = value.strftime(datetime_format)
        elif isinstance(value, tuple) and all(isinstance(item, datetime) for item in value):
            data[field] = tuple(map(lambda x: x.strftime(datetime_format), value))


async def create_task_instance_log(log_data: dict[str, Any]) -> None:
    """
    Создание лога изменений инстанса задачи
    """
    resources: dict[str, Any] = dict(
        task_instance_log_repo=TaskInstanceLogRepo,
    )
    create_log: loggers.CreateTaskInstanceLogLogger = loggers.CreateTaskInstanceLogLogger(**resources)
    await create_log(log_data=log_data)
