from http import HTTPStatus
from typing import Any
from fastapi import (APIRouter, Body, Path, Depends, Query)

from common import dependencies
from config import amocrm_config
from src.task_management.model import (
    TaskInstanceUpdateSchema,
    TaskChainStatusesResponseSchema,
    UpdateTaskResponseSchema,
    GetTaskResponseSchema,
)
from src.task_management.repos import TaskInstanceRepo, TaskStatusRepo
from src.task_management.use_cases import (
    TaskChainStatusesCase,
    UpdateTaskInstanceCase,
    SetPreviousTaskStatusCase,
    GetTaskInstanceCase,
)
from src.task_management.tasks import create_task_instance_task


router = APIRouter(prefix="/task_management", tags=["Цепочки задач"])


@router.patch(
    "/task_instance/{task_instance_id}",
    status_code=HTTPStatus.OK,
    dependencies=[Depends(dependencies.CurrentAnyTypeUserId())],
    response_model=UpdateTaskResponseSchema | None,
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


@router.get(
    "/task_instance/{task_instance_id}",
    status_code=HTTPStatus.OK,
    dependencies=[Depends(dependencies.CurrentAnyTypeUserId())],
    response_model=GetTaskResponseSchema | None,
)
async def get_task_instance(
    task_instance_id: int = Path(...),
):
    """
    Получение экземпляра задания
    """
    resources: dict[str, Any] = dict(
        task_instance_repo=TaskInstanceRepo,
    )

    get_task: GetTaskInstanceCase = GetTaskInstanceCase(**resources)
    return await get_task(task_id=task_instance_id)


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
    # from src.task_management.dto import CreateTaskDTO, UpdateTaskDTO
    from src.booking.repos import BookingRepo, Booking
    from src.booking.constants import BookingSubstages
    from src.users.constants import UserType
    from src.users.repos import UserRepo, CheckRepo
    from src.admins.repos import AdminRepo
    from src.users import services as user_services
    from src.users import repos as users_repos
    from src.notifications import services as notification_services
    from src.notifications import repos as notifications_repos
    from common.email import EmailService
    from src.projects.repos import ProjectRepo
    from src.booking.tasks import check_booking_task
    from datetime import datetime, timedelta
    from pytz import UTC
    from common.depreg import DepregAPI
    from src.task_management.repos import TaskInstanceRepo, ButtonDetailViewRepo
    from src.task_management.constants import OnlineBookingSlug
    from src.events_list.repos import EventParticipantListRepo, EventParticipantList
    from src.task_management.factories import CreateTaskInstanceServiceFactory
    from common import amocrm
    from common.amocrm.types import AmoLead
    from pprint import pprint
    from src.properties.repos import PropertyRepo, Property
    from src.amocrm.repos import AmocrmStatusRepo, AmocrmStatus
    from src.booking.tasks import check_booking_task
    from src.task_management.utils import get_booking_task, get_booking_tasks
    from src.task_management.repos import TaskInstanceRepo, TaskInstance

    task: TaskInstance = await get_booking_task(
        booking_id=5777,
        task_chain_slug=OnlineBookingSlug.PAYMENT.value,
    )
    print(f'{task=}')
    print(f'{task.id=}')


    # check_booking_task.delay(booking_id=5777)

    # amocrm_status: AmocrmStatus = await AmocrmStatusRepo().retrieve(
    #     filters=dict(
    #         name=BookingSubstages.BOOKING_LABEL,
    #         pipeline_id=3934218,
    #     ),
    # )
    # print(f'{amocrm_status=}')
    # print(f'{amocrm_status.id=}')
    #
    # booking_data: dict[str, Any] = dict(
    #     user_id=5142,
    #     agent_id=5137,
    #     project_id=5,
    #     amocrm_status=amocrm_status,
    #     payment_order_number="9c955ede-c482-42d0-a00b-ea50dacbeb70",
    # )
    #
    # booking: Booking = await BookingRepo().create(data=booking_data)
    #
    # create_task_instance = CreateTaskInstanceServiceFactory.create()
    # await create_task_instance(booking_ids=booking.id)
    # booking: dict[str, Any] = dict(booking)
    # booking["tasks"] = await get_booking_tasks(
    #     booking_id=booking["id"], task_chain_slug=OnlineBookingSlug.ACCEPT_OFFER.value
    # )
    # return booking



    # participant: EventParticipantList = await EventParticipantListRepo().retrieve(
    #     filters=dict(phone="7999999999"),
    #     related_fields=["event"],
    # )
    # print(f'{participant=}')
    # print(f'{datetime.today()=}')
    # print(f'{participant.event.event_date.date()=}')
    # if datetime.today().date() == participant.event.event_date.date():
    #     print("OK")


    # eta = datetime.now(tz=UTC) + timedelta(seconds=3)
    # print(f'{eta=}')
    #
    # check_booking_task.apply_async((5777,), eta=eta)
    # req = DepregAPI()
    # async with req as resp:
    #     res = await resp.get_participants(event_id=1471)
    # print(f'{res=}')

    # check_booking_task.delay(booking_id=5777)
    # check_booking_task.apply_async((booking.id,), eta=booking.expires)

    #
    # filters: dict[str, Any] = dict(active=True, user_id=5142, agent_id=5137)
    # bookings: list[Booking] = await BookingRepo().list(filters=filters)
    # print(f'{bookings=}')
    # active_projects: list[int] = [5]
    # booking_projects: set = {booking.project_id for booking in bookings}
    # print(f'{booking_projects=}')
    # not_created_project_ids = set(active_projects).difference(booking_projects)
    # print(f'{not_created_project_ids=}')
    # rsult = await ProjectRepo().list(
    #     filters=dict(id__in=not_created_project_ids),
    #     related_fields=["city"]
    # )
    # print(f'{rsult=}')



    # booking: Booking = await BookingRepo().retrieve(filters=dict(id=5777))

    # property_ = dict(property_id=None)
    # await BookingRepo().update(model=booking, data=property_)
    # await BookingRepo().update_or_create(filters=dict(id=5777), data=property_)
    # booking.property = None
    # await booking.save()

    # booking_notification_sms_task.delay(booking_id=5777)
    #
    # create_task = CreateTaskInstanceServiceFactory().create()
    # task_context: CreateTaskDTO = CreateTaskDTO()
    # # task_context.status_slug = 'pinning'
    # # task_context.status_slug = 123
    # task_context.booking_created = True
    # await create_task(booking_ids=[5777], task_context=task_context)
    # booking_notification_sms_task.delay(booking_id=5777)

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
    semaphore = asyncio.Semaphore(RATE_LIMIT)

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


@router.get("/close_old_booking_task", status_code=HTTPStatus.OK)
async def close_old_booking_view(
    debug: bool = Query(default=False),
    days: int = Query(default=50),
):
    """
    Одноразовый эндпоинт. Удалить после использования.
    Закрытие всех старых сделок.
    """
    from common.amocrm import amocrm
    from src.task_management.use_cases import CloseOldBookingCase
    from src.booking import repos as booking_repos

    resources: dict[str, Any] = dict(
        amocrm_class=amocrm.AmoCRM,
        booking_repo=booking_repos.BookingRepo,
    )

    close_old_bookings: CloseOldBookingCase = CloseOldBookingCase(**resources)
    return await close_old_bookings(days, debug)
