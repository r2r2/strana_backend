from copy import copy
from typing import Optional, Any, Callable
from datetime import datetime, timedelta
from pytz import UTC

import structlog

from common.sensei import SenseiAPI
from common.settings.repos import BookingSettingsRepo, BookingSettings
from src.booking.exceptions import BookingNotFoundError
from src.booking.repos import BookingRepo, Booking
from src.booking.types import BookingORM
from src.booking.loggers import booking_changes_logger
from src.task_management.constants import (PackageOfDocumentsSlug, FixationExtensionSlug,
                                           BOOKING_UPDATE_FIXATION_STATUSES)
from src.task_management.helpers import Slugs
from src.task_management.entities import BaseTaskService
from src.task_management.exceptions import TaskStatusNotFoundError
from src.task_management.loggers import task_instance_logger
from src.task_management.repos import TaskInstanceRepo, TaskStatusRepo, TaskStatus, TaskInstance


class UpdateTaskInstanceStatusService(BaseTaskService):
    """
    Обновление статуса задачи
    """

    def __init__(
        self,
        task_instance_repo: type[TaskInstanceRepo],
        task_status_repo: type[TaskStatusRepo],
        booking_repo: type[BookingRepo],
        booking_settings_repo: type[BookingSettingsRepo],
        update_task_instance_status_task: Any,
        booking_fixation_notification_email_task: Any,
        orm_class: Optional[BookingORM] = None,
        orm_config: Optional[dict[str, Any]] = None,
    ):
        self.task_instance_repo = task_instance_repo()
        self.task_status_repo = task_status_repo()
        self.booking_repo = booking_repo()
        self.orm_class: Optional[type[BookingORM]] = orm_class
        self.orm_config: Optional[dict[str, Any]] = copy(orm_config)
        self.booking_settings_repo: BookingSettingsRepo = booking_settings_repo()
        self.update_task_instance_status_task = update_task_instance_status_task
        self.booking_fixation_notification_email_task = booking_fixation_notification_email_task
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

        self.sensei: type[SenseiAPI] = SenseiAPI
        self.logger = structlog.get_logger()
        self.update_task = task_instance_logger(self.task_instance_repo.update, self, content="Обновление задачи")
        self.booking_update: Callable = booking_changes_logger(
            self.booking_repo.update, self, content="Обновление бронирования при изменении статуса задачи фиксации",
        )

    async def __call__(
        self,
        booking_id: int,
        status_slug: str,
        comment: Optional[str] = None,
        by_button: Optional[bool] = None,
    ) -> None:
        self.logger.info("Обновление статуса задачи:")
        booking, task_status = await self._get_booking_and_task_status(booking_id, status_slug)
        task_instances: list[TaskInstance] = booking.task_instances  # type: ignore
        self.logger.info(f"Найдено {len(task_instances)} задач(и) для сделки {booking}")

        slug_values: list[str] = Slugs.get_slug_values(status_slug)
        for task_instance in task_instances:
            # У сделки может быть несколько задач в разных цепочках задач
            # Поэтому проверяем, что статус задачи относится к нужной цепочке заданий
            if task_instance.status.slug in slug_values:
                task_amocrmid: Optional[int] = None
                if status_slug == PackageOfDocumentsSlug.CHECK.value:
                    task_amocrmid = await self._send_sensei_request(
                        sensei_pid=task_status.tasks_chain.sensei_pid,
                        amocrm_id=booking.amocrm_id
                    )

                elif status_slug == FixationExtensionSlug.DEAL_NEED_EXTENSION.value:
                    task_status = await self._get_task_status_for_need_extension_slug(
                        task_instance=task_instance,
                        task_status=task_status,
                        booking=booking,
                    )

                elif status_slug == FixationExtensionSlug.NO_EXTENSION_NEEDED.value:
                    task_status, task_amocrmid = await self._get_task_info_for_no_extension_needed_slug(
                        task_instance=task_instance,
                        task_status=task_status,
                        task_amocrmid=task_amocrmid,
                        booking=booking,
                        by_button=by_button,
                    )

                elif status_slug == FixationExtensionSlug.CANT_EXTEND_DEAL_BY_DATE.value:
                    if booking.fixation_expires > datetime.now(tz=UTC) or task_instance.status.slug in [
                        FixationExtensionSlug.DEAL_ALREADY_BOOKED.value,
                        FixationExtensionSlug.CANT_EXTEND_DEAL_BY_DATE.value,
                        FixationExtensionSlug.CANT_EXTEND_DEAL_BY_ATTEMPT.value,
                    ]:
                        task_status = None

                elif status_slug == FixationExtensionSlug.DEAL_ALREADY_BOOKED.value:
                    if task_instance.status.slug in [
                        FixationExtensionSlug.DEAL_ALREADY_BOOKED.value,
                        FixationExtensionSlug.CANT_EXTEND_DEAL_BY_DATE.value,
                        FixationExtensionSlug.CANT_EXTEND_DEAL_BY_ATTEMPT.value,
                    ]:
                        task_status = None

                if task_status:
                    data: dict[str, Any] = dict(
                        status=task_status,
                        comment=comment,
                        task_amocrmid=task_amocrmid,
                    )
                    self.logger.info(f"Обновление задачи {task_instance}: "
                                     f"Данные: {data}")
                    await self.update_task(task_instance=task_instance, data=data)

                # У сделки может быть только одна задача в цепочке задач, поэтому выходим из цикла
                break

    async def _get_task_status_for_need_extension_slug(
        self,
        task_instance: TaskInstance,
        task_status: TaskStatus,
        booking: Booking,
    ) -> Optional[TaskStatus]:
        booking_settings: BookingSettings = await self.booking_settings_repo.list().first()
        if task_instance.status.slug not in [
            FixationExtensionSlug.NO_EXTENSION_NEEDED.value,
            FixationExtensionSlug.DEAL_NEED_EXTENSION.value,
        ]:
            task_status = None
        elif (
            booking.amocrm_status
            and booking.amocrm_status.group_status
            and booking.amocrm_status.group_status.name not in BOOKING_UPDATE_FIXATION_STATUSES
        ):
            task_status = await self._get_only_task_status(
                status_slug=FixationExtensionSlug.DEAL_ALREADY_BOOKED.value,
            )
        elif booking.extension_number < 1:
            task_status = await self._get_only_task_status(
                status_slug=FixationExtensionSlug.CANT_EXTEND_DEAL_BY_ATTEMPT.value,
            )
        elif booking.fixation_expires < datetime.now(tz=UTC):
            task_status = await self._get_only_task_status(
                status_slug=FixationExtensionSlug.CANT_EXTEND_DEAL_BY_DATE.value,
            )
        elif (
            booking.fixation_expires - timedelta(days=booking_settings.extension_deadline)
        ) >= datetime.now(tz=UTC):
            task_status = None
        else:
            # оставляем task_status, полученный по переданному status_slug
            # создаем отложенную задачу на изменение статуса по истечению дедлайна фиксации
            self.update_task_instance_status_task.apply_async(
                (booking.id, FixationExtensionSlug.CANT_EXTEND_DEAL_BY_DATE.value),
                eta=booking.fixation_expires,
            )
            # запускаем отложенные таски по отправке писем за N часов до окончания фиксации
            # и при окончании фиксации
            self.booking_fixation_notification_email_task.delay(booking_id=booking.id)

        return task_status

    async def _get_task_info_for_no_extension_needed_slug(
        self,
        task_instance: TaskInstance,
        task_status: TaskStatus,
        task_amocrmid: Optional[int],
        booking: Booking,
        by_button: Optional[bool],
    ) -> tuple:
        if task_instance.status.slug not in [
            FixationExtensionSlug.NO_EXTENSION_NEEDED.value,
            FixationExtensionSlug.DEAL_NEED_EXTENSION.value,
        ]:
            task_status = None
        else:
            booking_settings: BookingSettings = await self.booking_settings_repo.list().first()
            # продление фиксации по кнопке (переход из статуса продления)
            if by_button:
                # обновляем поля в сделке для сохранения инфо о количестве продлений и дате окончания фиксации
                booking_data = dict(
                    extension_number=booking.extension_number - 1,
                    fixation_expires=booking.fixation_expires + timedelta(
                        days=booking_settings.updated_lifetime
                    ),
                )
                await self.booking_update(booking=booking, data=booking_data)

                # создаем отложенную задачу на изменение статуса задачи сделки фиксации,
                # когда продленная фиксация подходит к концу
                update_task_date = booking.fixation_expires - timedelta(
                    days=booking_settings.extension_deadline
                )
                self.update_task_instance_status_task.apply_async(
                    (booking.id, FixationExtensionSlug.DEAL_NEED_EXTENSION.value),
                    eta=update_task_date,
                )

                # продлеваем фиксацию в АМО
                task_amocrmid = await self._send_sensei_request(
                    sensei_pid=task_status.tasks_chain.sensei_pid,
                    amocrm_id=booking.amocrm_id,
                )
            else:
                task_date = booking.fixation_expires - timedelta(booking_settings.extension_deadline)
                self.update_task_instance_status_task.apply_async(
                    (booking.id, FixationExtensionSlug.DEAL_NEED_EXTENSION.value),
                    eta=task_date,
                )

        return task_status, task_amocrmid

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
            prefetch_fields=[
                "task_instances",
                "task_instances__status",
                "amocrm_status",
                "amocrm_status__group_status",
            ],
        )
        if not booking:
            raise BookingNotFoundError
        self.logger.info(f"Бронирование: {booking}")

        task_status: TaskStatus = await self.task_status_repo.retrieve(
            filters=dict(slug=status_slug),
            related_fields=["tasks_chain"]
        )
        if not task_status:
            raise TaskStatusNotFoundError
        self.logger.info(f"Статус задачи: {task_status}")
        return booking, task_status

    async def _get_only_task_status(
        self,
        status_slug: str
    ) -> TaskStatus:
        """
        Получение статуса задачи
        """
        task_status: TaskStatus = await self.task_status_repo.retrieve(
            filters=dict(slug=status_slug),
            related_fields=["tasks_chain"]
        )
        if not task_status:
            raise TaskStatusNotFoundError
        self.logger.info(f"Статус задачи: {task_status}")
        return task_status

    async def _send_sensei_request(self, sensei_pid: int, amocrm_id: int = None) -> Optional[int]:
        """
        Отправка запроса в сенсей
        """
        if not amocrm_id:
            return
        async with self.sensei() as sensei:
            self.logger.info(f'Sending request to SenseiAPI: {amocrm_id}')
            response = await sensei.process_start(
                process_id=sensei_pid,
                amocrm_id=amocrm_id,
            )
            self.logger.info(f'SenseiAPI response: {response}')
            try:
                return response.get('data')[0].get('instance_data').get('id')
            except (AttributeError, IndexError, TypeError) as exc:
                self.logger.warning(f'Error in SenseiAPI response: {exc}')
                return
