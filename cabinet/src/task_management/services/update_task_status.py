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
from src.task_management.dto import UpdateTaskDTO
from src.task_management.helpers import Slugs
from src.task_management.entities import BaseTaskService
from src.task_management.exceptions import TaskStatusNotFoundError
from src.task_management.loggers import task_instance_logger
from src.task_management.repos import TaskInstanceRepo, TaskStatusRepo, TaskStatus, TaskInstance


class UpdateTaskInstanceStatusService(BaseTaskService):
    """
    Обновление статуса задачи
    """
    # Context for task, could be used in task creation
    _task_context: UpdateTaskDTO

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

        self.task_instance: Optional[TaskInstance] = None
        self.booking: Optional[Booking] = None
        self.task_status: Optional[TaskStatus] = None
        self.task_amocrmid: Optional[int] = None

    async def __call__(
        self,
        booking_id: int,
        status_slug: list[str] | str,
        task_context: UpdateTaskDTO | None = None,
    ) -> None:
        self.logger.info("Обновление статуса задачи:")
        await self._set_booking(booking_id)
        self._task_context: UpdateTaskDTO = task_context if task_context else UpdateTaskDTO()
        _status_slugs: list[str] | str = status_slug if isinstance(status_slug, list) else [status_slug]
        task_instances: list[TaskInstance] = self.booking.task_instances  # type: ignore
        self.logger.info(f"Найдено {len(task_instances)} задач(и) для сделки {self.booking}")

        for status_slug in _status_slugs:
            await self._set_task_status(status_slug)
            task_chain_slugs: list[str] = Slugs.get_slug_values(status_slug)
            for task_instance in task_instances:
                self.task_instance: TaskInstance = task_instance
                # У сделки может быть несколько задач в разных цепочках задач
                # Поэтому проверяем, что статус задачи относится к нужной цепочке заданий
                if await self.should_handle_task(task_chain_slugs):
                    await self.handle_task_status(status_slug)
                    # У сделки может быть только одна задача в цепочке задач, поэтому выходим из цикла
                    break

    async def should_handle_task(self, task_chain_slugs: list[str]) -> bool:
        """
        Проверка, относится ли задача к нужной цепочке задач
        """
        return self.task_instance.status.slug in task_chain_slugs

    async def handle_task_status(self, status_slug: str) -> None:
        status_handlers: dict[str, Callable] = {
            PackageOfDocumentsSlug.CHECK.value: self.handle_check_status,
            FixationExtensionSlug.DEAL_NEED_EXTENSION.value: self.handle_deal_need_extension_status,
            FixationExtensionSlug.NO_EXTENSION_NEEDED.value: self.handle_no_extension_needed_status,
            FixationExtensionSlug.CANT_EXTEND_DEAL_BY_DATE.value: self.handle_cant_extend_by_date_status,
            FixationExtensionSlug.DEAL_ALREADY_BOOKED.value: self.handle_deal_already_booked_status,
        }

        if handler := status_handlers.get(status_slug):
            await handler()

        if self.task_status:
            data: dict[str, Any] = dict(
                status=self.task_status,
                comment=self._task_context.comment,
                task_amocrmid=self.task_amocrmid,
                current_step=self.task_instance.status.slug,
            )
            self.logger.info(f"Обновление задачи {self.task_instance}: "
                             f"Данные: {data}")
            await self.update_task(task_instance=self.task_instance, data=data)

    async def handle_check_status(self) -> None:
        """
        Кейс для статуса задачи пакета документов 'CHECK'
        """
        await self._send_sensei_request()

    async def handle_cant_extend_by_date_status(self) -> None:
        """
        Кейс для статуса задачи фиксации, когда сделка не может быть продлена из-за даты дедлайна
        """
        if self.booking.fixation_expires > datetime.now(tz=UTC) or self.task_instance.status.slug in [
            FixationExtensionSlug.DEAL_ALREADY_BOOKED.value,
            FixationExtensionSlug.CANT_EXTEND_DEAL_BY_DATE.value,
            FixationExtensionSlug.CANT_EXTEND_DEAL_BY_ATTEMPT.value,
        ]:
            self.task_status = None

    async def handle_deal_already_booked_status(self) -> None:
        """
        Кейс для статуса задачи фиксации, когда сделка прошла статус бронирования
        """
        if self.task_instance.status.slug in [
            FixationExtensionSlug.DEAL_ALREADY_BOOKED.value,
            FixationExtensionSlug.CANT_EXTEND_DEAL_BY_DATE.value,
            FixationExtensionSlug.CANT_EXTEND_DEAL_BY_ATTEMPT.value,
        ]:
            self.task_status = None

    async def handle_deal_need_extension_status(self) -> None:
        """
        Кейс для статуса задачи фиксации, когда сделка нуждается в продлении
        """
        booking_settings: BookingSettings = await self.booking_settings_repo.list().first()
        if self.task_instance.status.slug not in [
            FixationExtensionSlug.NO_EXTENSION_NEEDED.value,
            FixationExtensionSlug.DEAL_NEED_EXTENSION.value,
        ]:
            self.task_status = None
        elif (
            self.booking.amocrm_status
            and self.booking.amocrm_status.group_status
            and self.booking.amocrm_status.group_status.name not in BOOKING_UPDATE_FIXATION_STATUSES
        ):
            await self._set_task_status(
                status_slug=FixationExtensionSlug.DEAL_ALREADY_BOOKED.value,
            )
        elif self.booking.extension_number < 1:
            await self._set_task_status(
                status_slug=FixationExtensionSlug.CANT_EXTEND_DEAL_BY_ATTEMPT.value,
            )
        elif self.booking.fixation_expires < datetime.now(tz=UTC):
            await self._set_task_status(
                status_slug=FixationExtensionSlug.CANT_EXTEND_DEAL_BY_DATE.value,
            )
        elif (
            self.booking.fixation_expires - timedelta(days=booking_settings.extension_deadline)
        ) >= datetime.now(tz=UTC):
            self.task_status = None
        else:
            # оставляем task_status, полученный по переданному status_slug
            # создаем отложенную задачу на изменение статуса по истечению дедлайна фиксации
            self.update_task_instance_status_task.apply_async(
                (self.booking.id, FixationExtensionSlug.CANT_EXTEND_DEAL_BY_DATE.value),
                eta=self.booking.fixation_expires,
            )
            # запускаем отложенные таски по отправке писем за N часов до окончания фиксации
            # и при окончании фиксации
            self.booking_fixation_notification_email_task.delay(booking_id=self.booking.id)

    async def handle_no_extension_needed_status(self) -> None:
        """
        Кейс для статуса задачи фиксации, когда продление не требуется
        """
        if self.task_instance.status.slug not in [
            FixationExtensionSlug.NO_EXTENSION_NEEDED.value,
            FixationExtensionSlug.DEAL_NEED_EXTENSION.value,
        ]:
            self.task_status = None
        else:
            booking_settings: BookingSettings = await self.booking_settings_repo.list().first()
            # продление фиксации по кнопке (переход из статуса продления)
            if self._task_context.by_button:
                # обновляем поля в сделке для сохранения инфо о количестве продлений и дате окончания фиксации
                booking_data = dict(
                    extension_number=self.booking.extension_number - 1,
                    fixation_expires=self.booking.fixation_expires + timedelta(
                        days=booking_settings.updated_lifetime
                    ),
                )
                await self.booking_update(booking=self.booking, data=booking_data)

                # создаем отложенную задачу на изменение статуса задачи сделки фиксации,
                # когда продленная фиксация подходит к концу
                update_task_date: datetime = self.booking.fixation_expires - timedelta(
                    days=booking_settings.extension_deadline
                )
                self.update_task_instance_status_task.apply_async(
                    (self.booking.id, FixationExtensionSlug.DEAL_NEED_EXTENSION.value),
                    eta=update_task_date,
                )

                # продлеваем фиксацию в АМО
                await self._send_sensei_request()
            else:
                task_date: datetime = self.booking.fixation_expires - timedelta(
                    days=booking_settings.extension_deadline
                )
                self.update_task_instance_status_task.apply_async(
                    (self.booking.id, FixationExtensionSlug.DEAL_NEED_EXTENSION.value),
                    eta=task_date,
                )

    async def _set_booking(self, booking_id: int) -> None:
        """
        Получение бронирования
        """
        self.booking: Booking = await self.booking_repo.retrieve(
            filters=dict(id=booking_id),
            prefetch_fields=[
                "task_instances__status",
                "amocrm_status__group_status",
            ],
        )
        if not self.booking:
            raise BookingNotFoundError
        self.logger.info(f"Бронирование: {self.booking}")

    async def _set_task_status(self, status_slug: str) -> None:
        """
        Получение статуса задачи
        """
        self.task_status: TaskStatus = await self.task_status_repo.retrieve(
            filters=dict(slug=status_slug),
            related_fields=["tasks_chain"]
        )
        if not self.task_status:
            raise TaskStatusNotFoundError
        self.logger.info(f"Статус задачи: {self.task_status}")

    async def _send_sensei_request(self) -> bool:
        """
        Отправка запроса в сенсей
        Устанавливает task_amocrmid
        """
        if not self.booking.amocrm_id:
            return False
        async with self.sensei() as sensei:
            self.logger.info(f'Sending request to SenseiAPI: {self.booking.amocrm_id}')
            response = await sensei.process_start(
                process_id=self.task_status.tasks_chain.sensei_pid,
                amocrm_id=self.booking.amocrm_id,
            )
            self.logger.info(f'SenseiAPI response: {response}')
            try:
                self.task_amocrmid: int = response.get('data')[0].get('instance_data').get('id')
                return True
            except (AttributeError, IndexError, TypeError) as exc:
                self.logger.warning(f'Error in SenseiAPI response: {exc}')
                return False
