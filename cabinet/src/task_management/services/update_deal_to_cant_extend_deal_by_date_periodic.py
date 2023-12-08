from copy import copy
from typing import Optional, Any
from datetime import datetime, timedelta
from pytz import UTC

import structlog

from config import celery_config
from src.booking.types import BookingORM
from src.task_management.constants import FixationExtensionSlug
from src.task_management.entities import BaseTaskService
from src.task_management.repos import TaskInstanceRepo, TaskInstance
from src.task_management.services import UpdateTaskInstanceStatusService


class UpdateDealToCantExtendDealByDateStatusService(BaseTaskService):
    """
    Периодический сервис обновления задач фиксаций, в статус,
    когда сделка нельзя продлить из-за даты окончания фиксации (через отложенные eta задачи).
    """

    def __init__(
        self,
        task_instance_repo: type[TaskInstanceRepo],
        update_status_service: UpdateTaskInstanceStatusService,
        update_task_instance_status_task: Any,
        orm_class: Optional[BookingORM] = None,
        orm_config: Optional[dict[str, Any]] = None,
    ):
        self.task_instance_repo = task_instance_repo()
        self.update_status_service: UpdateTaskInstanceStatusService = update_status_service
        self.update_task_instance_status_task = update_task_instance_status_task
        self.orm_class: Optional[type[BookingORM]] = orm_class
        self.orm_config: Optional[dict[str, Any]] = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

        self.logger = structlog.get_logger(self.__class__.__name__)
        self.fixations_statuses: type[FixationExtensionSlug] = FixationExtensionSlug

    async def __call__(self) -> None:
        # добавление в eta очередь задачи на обновление до статуса "невозможно продлить из-за даты" (точно по времени)
        deal_need_extension_task_filters = dict(
            booking__fixation_expires__gte=datetime.now(UTC),
            booking__fixation_expires__lte=datetime.now(UTC) + timedelta(
                hours=celery_config.get("periodic_eta_timeout_hours", 24)
            ),
            status__slug=self.fixations_statuses.DEAL_NEED_EXTENSION.value,
        )
        deal_need_extension_task_instances: list[TaskInstance] = await self.task_instance_repo.list(
            filters=deal_need_extension_task_filters,
            prefetch_fields=["booking", "status"],
        )
        self.logger.info(
            f"Задачи, которые через сутки требуют изменения статуса на 'невозможно продлить из-за даты' в количестве - "
            f"{len(deal_need_extension_task_instances) if deal_need_extension_task_instances else 0 } шт"
        )
        for task_instance in deal_need_extension_task_instances:
            self.update_task_instance_status_task.apply_async(
                (
                    task_instance.booking.id,
                    self.fixations_statuses.CANT_EXTEND_DEAL_BY_DATE.value,
                    None,
                    self.__class__.__name__,
                ),
                eta=task_instance.booking.fixation_expires,
                queue="scheduled",
            )
            self.logger.info(
                f"Задача {task_instance} добавлена в eta очередь на обработку для изменения статуса "
                f"на 'невозможно продлить из-за даты'"
            )

        # находим задачи, которые по каким-то причинам остались в старом статусе "требуется продление" после даты
        # окончания фиксации и актуализируем их
        cant_extend_by_date_task_filters = dict(
            booking__fixation_expires__lte=datetime.now(UTC),
            status__slug=self.fixations_statuses.DEAL_NEED_EXTENSION.value,
        )
        cant_extend_by_date_task_instances: list[TaskInstance] = await self.task_instance_repo.list(
            filters=cant_extend_by_date_task_filters,
            prefetch_fields=["booking", "status"],
        )
        self.logger.info(
            f"Задачи, которые остались в старом старом статусе 'требуется продление' "
            f"после даты окончания фиксации в количестве - "
            f"{len(cant_extend_by_date_task_instances) if cant_extend_by_date_task_instances else 0} шт"
        )
        for task_instance in cant_extend_by_date_task_instances:
            await self.update_status_service(
                booking_id=task_instance.booking.id,
                status_slug=self.fixations_statuses.CANT_EXTEND_DEAL_BY_DATE.value,
            )
            self.logger.info(f"Для задачи {task_instance} актуализирован статус на 'невозможно продлить из-за даты'")
