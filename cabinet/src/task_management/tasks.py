from asyncio import get_event_loop
from typing import Any

from tortoise import Tortoise

from config import celery, tortoise_config
from src.task_management import repos as task_management_repos
from src.task_management import loggers
from src.task_management import services
from src.task_management.dto import UpdateTaskDTO, CreateTaskDTO
from src.task_management.factories import CreateTaskInstanceServiceFactory, UpdateTaskInstanceStatusServiceFactory
from icecream import ic


@celery.app.task
def create_task_instance_task(booking_ids: list[int], task_context: CreateTaskDTO | None = None) -> None:
    """
    Создание инстанса задачи для цепочки заданий
    """
    create_task_instance_service: services.CreateTaskInstanceService = CreateTaskInstanceServiceFactory.create()
    loop: Any = get_event_loop()
    loop.run_until_complete(
        celery.sentry_catch(celery.init_orm(create_task_instance_service))(
            booking_ids=booking_ids, task_context=task_context
        )
    )


@celery.app.task
def update_task_instance_status_task(
    booking_id: int,
    status_slug: str,
    task_context: UpdateTaskDTO | None = None,
    caller_info: str | None = None,
) -> None:
    """
    Обновление статуса инстанса задачи
    """
    ic(caller_info)
    update_status_service: services.UpdateTaskInstanceStatusService = UpdateTaskInstanceStatusServiceFactory.create()
    loop: Any = get_event_loop()
    loop.run_until_complete(
        celery.sentry_catch(celery.init_orm(update_status_service))(
            booking_id=booking_id, status_slug=status_slug, task_context=task_context
        )
    )


@celery.app.task
def create_task_instance_log_task(log_data: dict[str, Any]) -> None:
    """
    Создание лога изменений инстанса задачи
    """
    resources: dict[str, Any] = dict(
        task_instance_log_repo=task_management_repos.TaskInstanceLogRepo,
        orm_class=Tortoise,
        orm_config=tortoise_config,
    )
    create_log: loggers.CreateTaskInstanceLogLogger = loggers.CreateTaskInstanceLogLogger(
        **resources
    )
    loop: Any = get_event_loop()
    loop.run_until_complete(celery.sentry_catch(celery.init_orm(create_log))(log_data=log_data))
