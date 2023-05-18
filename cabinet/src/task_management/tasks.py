from asyncio import get_event_loop
from typing import Any, Optional

from tortoise import Tortoise

from config import celery, tortoise_config
from src.booking import repos as booking_repos
from src.task_management import repos as task_management_repos
from src.task_management import services


@celery.app.task
def create_task_instance_task(booking_ids: list[int]) -> None:
    """
    Создание инстанса задачи для цепочки заданий
    """
    resources: dict[str, Any] = dict(
        orm_class=Tortoise,
        orm_config=tortoise_config,
        booking_repo=booking_repos.BookingRepo,
        task_instance_repo=task_management_repos.TaskInstanceRepo,
        task_chain_repo=task_management_repos.TaskChainRepo,
        task_status_repo=task_management_repos.TaskStatusRepo,
    )
    create_task_instance_case: services.CreateTaskInstanceService = services.CreateTaskInstanceService(
        **resources
    )
    loop: Any = get_event_loop()
    loop.run_until_complete(
        celery.sentry_catch(celery.init_orm(create_task_instance_case))(booking_ids=booking_ids)
    )


@celery.app.task
def update_task_instance_status_task(
    booking_id: int,
    status_slug: str,
    comment: Optional[str] = None,
) -> None:
    """
    Обновление статуса инстанса задачи
    """
    resources: dict[str, Any] = dict(
        orm_class=Tortoise,
        orm_config=tortoise_config,
        task_instance_repo=task_management_repos.TaskInstanceRepo,
        task_status_repo=task_management_repos.TaskStatusRepo,
        booking_repo=booking_repos.BookingRepo,
    )
    update_status_service: services.UpdateTaskInstanceStatusService = services.UpdateTaskInstanceStatusService(
        **resources
    )
    loop: Any = get_event_loop()
    loop.run_until_complete(
        celery.sentry_catch(celery.init_orm(update_status_service))(
            booking_id=booking_id, status_slug=status_slug, comment=comment,
        )
    )
