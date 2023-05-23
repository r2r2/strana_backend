from copy import copy
from typing import Optional, Any

import structlog

from common.sensei import SenseiAPI
from src.booking.exceptions import BookingNotFoundError
from src.booking.repos import BookingRepo, Booking
from src.booking.types import BookingORM
from src.task_management.constants import PackageOfDocumentsSlug
from src.task_management.helpers import Slugs
from src.task_management.entities import BaseTaskService
from src.task_management.exceptions import TaskStatusNotFoundError
from src.task_management.repos import TaskInstanceRepo, TaskStatusRepo, TaskStatus


class UpdateTaskInstanceStatusService(BaseTaskService):
    """
    Обновление статуса задачи
    """

    def __init__(
        self,
        task_instance_repo: type[TaskInstanceRepo],
        task_status_repo: type[TaskStatusRepo],
        booking_repo: type[BookingRepo],
        orm_class: Optional[BookingORM] = None,
        orm_config: Optional[dict[str, Any]] = None,
    ):
        self.task_instance_repo = task_instance_repo()
        self.task_status_repo = task_status_repo()
        self.booking_repo = booking_repo()
        self.orm_class: Optional[type[BookingORM]] = orm_class
        self.orm_config: Optional[dict[str, Any]] = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

        self.sensei: type[SenseiAPI] = SenseiAPI
        self.logger = structlog.get_logger('errors')

    async def __call__(
        self,
        booking_id: int,
        status_slug: str,
        comment: Optional[str] = None
    ) -> None:
        booking, task_status = await self._get_booking_and_task_status(booking_id, status_slug)
        task_instances: list[TaskInstance] = booking.task_instances  # type: ignore

        slug_values: list[str] = Slugs.get_slug_values(status_slug)
        for task_instance in task_instances:
            # У сделки может быть несколько задач в разных цепочках задач
            # Поэтому проверяем, что статус задачи относится к нужной цепочке заданий
            if task_instance.status.slug in slug_values:
                task_amocrmid: Optional[int] = None
                if status_slug == PackageOfDocumentsSlug.CHECK.value:
                    task_amocrmid = await self._send_sensei_request(amocrm_id=booking.amocrm_id)

                data: dict[str, Any] = dict(
                    status=task_status,
                    comment=comment or task_instance.comment,
                    task_amocrmid=task_amocrmid,
                )
                await self.task_instance_repo.update(task_instance, data=data)
                # У сделки может быть только одна задача в цепочке задач, поэтому выходим из цикла
                break

    async def _get_booking_and_task_status(
        self,
        booking_id: int,
        status_slug: str
    ) -> tuple[Booking, TaskStatus]:
        """
        Получение бронирования и статуса задачи
        """
        booking: Booking = await self.booking_repo.retrieve(
            filters=dict(id=booking_id),
            prefetch_fields=["task_instances", "task_instances__status"],
        )
        if not booking:
            raise BookingNotFoundError

        task_status: TaskStatus = await self.task_status_repo.retrieve(
            filters=dict(slug=status_slug),
        )
        if not task_status:
            raise TaskStatusNotFoundError

        return booking, task_status

    async def _send_sensei_request(self, amocrm_id: int = None) -> Optional[int]:
        """
        Отправка запроса в сенсей
        """
        if not amocrm_id:
            return
        async with self.sensei() as sensei:
            self.logger.info(f'Sending request to SenseiAPI: {amocrm_id}')
            response = await sensei.process_start(
                process_id=sensei.SENSEI_PID,
                amocrm_id=amocrm_id,
            )
            self.logger.info(f'SenseiAPI response: {response}')
            try:
                return response.get('data')[0].get('instance_data').get('id')
            except (AttributeError, IndexError, TypeError) as exc:
                self.logger.warning(f'Error in SenseiAPI response: {exc}')
                return
