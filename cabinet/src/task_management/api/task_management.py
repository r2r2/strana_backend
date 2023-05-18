from http import HTTPStatus
from typing import Any
from urllib.parse import parse_qs, unquote

from fastapi import (APIRouter, Body, Path, Depends, Request)
from starlette.requests import ClientDisconnect

from common import dependencies
from src.booking.repos import BookingRepo
from src.task_management.model import TaskInstanceUpdateSchema
from src.task_management.repos import TaskInstanceRepo, TaskStatusRepo
from src.task_management import services as task_management_services
from src.task_management.use_cases import (
    UpdateTaskInstanceCase,
    AmoCRMWebhookUpdateTaskInstanceCase
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


@router.post("/amocrm/change_status", status_code=HTTPStatus.OK)
async def amocrm_webhook_change_status(request: Request) -> None:
    """
    Вебхук от АМО для обновления статуса задания
    """
    try:
        payload: bytes = await request.body()
    except ClientDisconnect:
        return
    data: dict[str, Any] = parse_qs(unquote(payload.decode("utf-8")))

    resources: dict[str, Any] = dict(
        task_instance_repo=TaskInstanceRepo,
        task_status_repo=TaskStatusRepo,
        booking_repo=BookingRepo,
    )
    update_task_instance_status_service = task_management_services.UpdateTaskInstanceStatusService(
        **resources
    )

    resources: dict[str, Any] = dict(
        booking_repo=BookingRepo,
        update_task_instance_status_service=update_task_instance_status_service,
    )
    update_task: AmoCRMWebhookUpdateTaskInstanceCase = AmoCRMWebhookUpdateTaskInstanceCase(**resources)
    await update_task(data=data)


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
