from asyncio import get_event_loop
from typing import Any, Optional

from tortoise import Tortoise

from config import celery, tortoise_config
from common.settings.repos import BookingSettingsRepo
from src.booking import repos as booking_repos
from src.task_management import repos as task_management_repos
from src.task_management import loggers
from src.task_management import services
from src.notifications.tasks import booking_fixation_notification_email_task


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
        booking_settings_repo=BookingSettingsRepo,
        update_task_instance_status_task=update_task_instance_status_task,
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
    by_button: Optional[bool] = None,
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
        booking_settings_repo=BookingSettingsRepo,
        update_task_instance_status_task=update_task_instance_status_task,
        booking_fixation_notification_email_task=booking_fixation_notification_email_task,
    )
    update_status_service: services.UpdateTaskInstanceStatusService = services.UpdateTaskInstanceStatusService(
        **resources
    )
    loop: Any = get_event_loop()
    loop.run_until_complete(
        celery.sentry_catch(celery.init_orm(update_status_service))(
            booking_id=booking_id, status_slug=status_slug, comment=comment, by_button=by_button
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
