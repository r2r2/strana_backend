from http import HTTPStatus
from typing import Any
from fastapi import (APIRouter, Body, Path, Depends, Query)

from common import dependencies
from config import amocrm_config
from src.task_management.model import TaskInstanceUpdateSchema, TaskChainStatusesResponseSchema
from src.task_management.repos import TaskInstanceRepo, TaskStatusRepo
from src.task_management.use_cases import (
    TaskChainStatusesCase,
    UpdateTaskInstanceCase,
    SetPreviousTaskStatusCase,
)
from src.task_management.tasks import create_task_instance_task


router = APIRouter(prefix="/task_management", tags=["Task Management"])


@router.patch(
    "/task_instance/{task_instance_id}",
    status_code=HTTPStatus.OK,
    dependencies=[Depends(dependencies.CurrentAnyTypeUserId())],
)
async def update_task_instance(
    task_instance_id: int = Path(...),
    payload: TaskInstanceUpdateSchema = Body(...),
):
    """
    Обновление экземпляра задания
    """
    resources: dict[str, Any] = dict(
        task_instance_repo=TaskInstanceRepo,
        task_status_repo=TaskStatusRepo,
    )

    update_task: UpdateTaskInstanceCase = UpdateTaskInstanceCase(**resources)
    return await update_task(payload=payload, task_instance_id=task_instance_id)


@router.post(
    "/admin/create_task_instance/{booking_id}",
    status_code=HTTPStatus.OK,
)
async def create_task_instance_from_admin(
    booking_id: int = Path(...),
):
    """
    Создание экземпляра задания из админки
    """
    create_task_instance_task.delay(booking_ids=[booking_id])


@router.get(
    "/task_chain/statuses",
    status_code=HTTPStatus.OK,
    response_model=list[TaskChainStatusesResponseSchema],
    dependencies=[Depends(dependencies.CurrentAnyTypeUserId())],
)
async def get_task_chain_statuses(
    slug: str = Query(...),
):
    """
    Получение статусов цепочки заданий
    @param slug: слаг статуса
    """
    get_all_statuses: TaskChainStatusesCase = TaskChainStatusesCase()
    return await get_all_statuses(slug=slug)


@router.post(
    "/tasks/{task_id}/previous_status",
    status_code=HTTPStatus.OK,
    dependencies=[Depends(dependencies.CurrentAnyTypeUserId())],
)
async def set_previous_status(
    task_id: int = Path(...),
):
    """
    Установка предыдущего статуса задания
    @param task_id: id задания
    """
    resources: dict[str, Any] = dict(
        task_instance_repo=TaskInstanceRepo,
    )

    set_status: SetPreviousTaskStatusCase = SetPreviousTaskStatusCase(**resources)
    await set_status(task_id=task_id)


@router.post(
    "/set_pinning",
    status_code=HTTPStatus.OK,
)
async def one_time_set_pinning():
    from fastapi import HTTPException
    from src.notifications.tasks import booking_notification_sms_task
    from src.task_management.factories import CreateTaskInstanceServiceFactory
    from src.task_management.dto import CreateTaskDTO, UpdateTaskDTO

    # booking_notification_sms_task.delay(booking_id=5777)

    create_task = CreateTaskInstanceServiceFactory().create()
    task_context: CreateTaskDTO = CreateTaskDTO()
    # task_context.status_slug = 'pinning'
    # task_context.status_slug = 123
    task_context.booking_created = True
    await create_task(booking_ids=[5777], task_context=task_context)

    raise HTTPException(status_code=418)
    """
    Одноразовый эндпоинт. Удалить после использования.
    Установка Статуса закрепления для всех пользователей
    """
    import asyncio
    import multiprocessing
    from time import time
    from common.amocrm import amocrm
    from src.users import repos as users_repos
    from src.users import services as users_services
    from src.users import constants as users_constants
    from src.users.constants import UserPinningStatusType

    RATE_LIMIT = 2  # requests per second

    resources: dict[str, Any] = dict(
        amocrm_class=amocrm.AmoCRM,
        user_repo=users_repos.UserRepo,
        check_pinning_repo=users_repos.PinningStatusRepo,
        user_pinning_repo=users_repos.UserPinningStatusRepo,
        amocrm_config=amocrm_config,
    )
    check_pinning: users_services.CheckPinningStatusService = users_services.CheckPinningStatusService(**resources)

    batch_size = 100
    concurrency_limit = multiprocessing.cpu_count()

    total_users_count = await users_repos.UserRepo().count(
        filters=dict(
            type=users_constants.UserType.CLIENT,
            users_checks__unique_status__slug=UserPinningStatusType.NOT_PINNED,
        ),
    )
    total_users_count = len(total_users_count)
    print("++++Start Task++++")
    print(f'Total users count: {total_users_count}')

    total_batches = (total_users_count + batch_size - 1) // batch_size
    semaphore = asyncio.Semaphore(concurrency_limit)

    async def process_batch(offset: int):
        start_time = time()
        users_to_check_ids = await (
            users_repos.User.all()
            .filter(
                type=users_constants.UserType.CLIENT,
                users_checks__unique_status__slug=UserPinningStatusType.NOT_PINNED,
            )
            .limit(batch_size)
            .offset(offset=offset)
            .only('id')
            .values_list('id', flat=True)
        )

        for user_id in users_to_check_ids:
            async with semaphore:
                await check_pinning(user_id=user_id)
                elapsed_time = time() - start_time
                if elapsed_time < 1 / RATE_LIMIT:
                    await asyncio.sleep(1 / RATE_LIMIT - elapsed_time)

    process_tasks = []
    for offset in range(0, total_batches * batch_size, batch_size):
        process_tasks.append(asyncio.create_task(process_batch(offset=offset)))

    print(f"{len(process_tasks)} tasks created")

    await asyncio.gather(*process_tasks)
    print("++++All Task Done++++")


@router.get("/add_booking_fixation_tasks", status_code=HTTPStatus.OK)
async def tip_list_view():
    """
    Одноразовый эндпоинт. Удалить после использования.
    Продление всех действующих сделок (задачи фиксации).
    """
    from src.task_management.use_cases import CreateTaskInstanceForOldBookingCase
    from src.task_management import repos as task_management_repos
    from src.booking import repos as booking_repos
    from common.settings.repos import BookingSettingsRepo
    from src.task_management.tasks import update_task_instance_status_task
    from src.notifications.tasks import booking_fixation_notification_email_task

    resources: dict[str, Any] = dict(
        task_instance_repo=task_management_repos.TaskInstanceRepo,
        task_status_repo=task_management_repos.TaskStatusRepo,
        task_chain_repo=task_management_repos.TaskChainRepo,
        booking_repo=booking_repos.BookingRepo,
        booking_settings_repo=BookingSettingsRepo,
        update_task_instance_status_task=update_task_instance_status_task,
        booking_fixation_notification_email_task=booking_fixation_notification_email_task,
    )

    create_task_for_old_bookings: CreateTaskInstanceForOldBookingCase = CreateTaskInstanceForOldBookingCase(**resources)
    return await create_task_for_old_bookings()
