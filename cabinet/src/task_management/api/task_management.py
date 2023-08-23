from http import HTTPStatus
from typing import Any
from fastapi import (APIRouter, Body, Path, Depends)

from common import dependencies
from config import amocrm_config
from src.task_management.model import TaskInstanceUpdateSchema
from src.task_management.repos import TaskInstanceRepo, TaskStatusRepo
from src.task_management.use_cases import (
    UpdateTaskInstanceCase,
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


@router.post(
    "/set_pinning",
    status_code=HTTPStatus.OK,
)
async def one_time_set_pinning():
    from fastapi import HTTPException
    from sentry_sdk import utils
    from sentry_sdk import capture_message
    import structlog
    print(f'{utils.MAX_STRING_LENGTH=}')

    logger = structlog.get_logger()
    capture_message('test')
    logger.exception('test*******test___________418')



    raise HTTPException(status_code=418, detail="Hello world, from FastAPI!")
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
