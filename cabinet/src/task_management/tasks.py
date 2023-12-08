from asyncio import get_event_loop
from typing import Any

from tortoise import Tortoise

from common.settings.repos import BookingSettingsRepo
from config import celery, tortoise_config
from src.task_management import repos as task_management_repos
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
def periodic_update_deal_to_need_extension_status_task() -> None:
    """
    Обновление задач фиксаций, в статус, когда сделка нуждается в продлении (через отложенные eta задачи).
    """

    resources: dict[str, Any] = dict(
        task_instance_repo=task_management_repos.TaskInstanceRepo,
        booking_settings_repo=BookingSettingsRepo,
        update_status_service=UpdateTaskInstanceStatusServiceFactory.create(),
        update_task_instance_status_task=update_task_instance_status_task,
        orm_class=Tortoise,
        orm_config=tortoise_config,
    )
    update_deal_to_need_extension_service: services.UpdateDealToNeedExtensionStatusService = \
        services.UpdateDealToNeedExtensionStatusService(
            **resources
        )
    loop: Any = get_event_loop()
    loop.run_until_complete(celery.sentry_catch(celery.init_orm(update_deal_to_need_extension_service))())


@celery.app.task
def periodic_update_deal_to_cant_extend_deal_by_date_task() -> None:
    """
    Обновление задач фиксаций, в статус, когда сделку нельзя продлить из-за даты окончания фиксации
    (через отложенные eta задачи).
    """

    resources: dict[str, Any] = dict(
        task_instance_repo=task_management_repos.TaskInstanceRepo,
        update_status_service=UpdateTaskInstanceStatusServiceFactory.create(),
        update_task_instance_status_task=update_task_instance_status_task,
        orm_class=Tortoise,
        orm_config=tortoise_config,
    )
    update_deal_to_cant_extend_deal_by_date_service: services.UpdateDealToCantExtendDealByDateStatusService = \
        services.UpdateDealToCantExtendDealByDateStatusService(
            **resources
        )
    loop: Any = get_event_loop()
    loop.run_until_complete(celery.sentry_catch(celery.init_orm(update_deal_to_cant_extend_deal_by_date_service))())
