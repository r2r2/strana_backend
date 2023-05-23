from http import HTTPStatus
from typing import Any
from fastapi import (APIRouter, Body, Path, Depends)

from common import dependencies
from src.booking.repos import BookingRepo
from src.task_management.model import TaskInstanceUpdateSchema
from src.task_management.repos import TaskInstanceRepo, TaskStatusRepo
from src.task_management import services as task_management_services
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
    "/create_tasks",
    status_code=HTTPStatus.OK,
)
async def endpoint_to_delete():
    """
    скрипт, который разово по всем сделкам пройдется и создаст задачу на платную бронь для всех сделок в фиксации за АН
    https://youtrack.artw.ru/issue/strana_lk-1403
    """
    import asyncio
    from src.task_management.repos import TaskChainRepo, TaskChain
    from src.booking.repos import Booking

    AMOCRMID = [
        50284815,
        51105825,
        41481162,
        57272745,
        55950761,
        51944400,
        51489690
    ]

    bookings: list[Booking] = await BookingRepo().list(
        filters=dict(amocrm_status_id__in=AMOCRMID)
    )

    resources: dict[str, Any] = dict(
        booking_repo=BookingRepo,
        task_instance_repo=TaskInstanceRepo,
        task_chain_repo=TaskChainRepo,
        task_status_repo=TaskStatusRepo,
    )
    create_task_instance = task_management_services.CreateTaskInstanceService(
        **resources
    )
    task_chain: TaskChain = await TaskChainRepo().retrieve(
        filters=dict(name__iexact="Зарезервировать квартиру")
    )
    tasks = []
    for booking in bookings:
        tasks.append(
            create_task_instance.paid_booking_case(booking=booking, task_chain=task_chain)
        )
    await asyncio.gather(*tasks)
