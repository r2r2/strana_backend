from datetime import datetime, timedelta
from typing import Any, Type

import structlog
from common.settings.repos import BookingSettings, BookingSettingsRepo
from pytz import UTC
from src.booking.repos import Booking, BookingRepo
from src.task_management.constants import (BOOKING_UPDATE_FIXATION_STATUSES,
                                           FixationExtensionSlug)
from src.task_management.exceptions import TaskStatusNotFoundError
from src.task_management.loggers import task_instance_logger
from src.task_management.repos import (TaskChain, TaskChainRepo, TaskInstance,
                                       TaskInstanceRepo, TaskStatus,
                                       TaskStatusRepo)


class CreateTaskInstanceForOldBookingCase:
    FIXATION_TASK_CHAIN_NAME = "Продление сделки"

    def __init__(
        self,
        task_instance_repo: Type[TaskInstanceRepo],
        task_status_repo: Type[TaskStatusRepo],
        task_chain_repo: Type[TaskChainRepo],
        booking_repo: Type[BookingRepo],
        booking_settings_repo: type[BookingSettingsRepo],
        update_task_instance_status_task: Any,
        booking_fixation_notification_email_task: Any,
    ):
        self.task_instance_repo: TaskInstanceRepo = task_instance_repo()
        self.task_status_repo: TaskStatusRepo = task_status_repo()
        self.task_chain_repo: TaskChainRepo = task_chain_repo()
        self.booking_repo: BookingRepo = booking_repo()
        self.booking_settings_repo: BookingSettingsRepo = booking_settings_repo()
        self.create_task = task_instance_logger(self.task_instance_repo.create, self, content="Создание задачи")
        self.update_task_instance_status_task: Any = update_task_instance_status_task
        self.booking_fixation_notification_email_task: Any = booking_fixation_notification_email_task
        self.logger = structlog.get_logger()

    async def __call__(self) -> None:
        self.logger.info("Запущен скрипт для создания инстансов задач фиксаций старых сделок")
        booking_settings: BookingSettings = await self.booking_settings_repo.list().first()
        no_extension_needed_bookings, extension_needed_bookings = await self._get_bookings(booking_settings)
        no_extension_needed_task_status, deal_need_extension_task_status = await self._get_task_statuses()

        self.logger.info("Создание задач для сделок не требующих продления:")
        self.logger.info(f"Старых сделок, не требующих продление фиксации - {len(no_extension_needed_bookings)}")
        for no_extension_needed_booking in no_extension_needed_bookings:
            await self._create_no_extension_needed_task_instance(
                booking=no_extension_needed_booking,
                task_status=no_extension_needed_task_status,
                booking_settings=booking_settings,
            )

        self.logger.info("Создание задач для сделок требующих продления:")
        self.logger.info(f"Старых сделок, требующих продление фиксации - {len(extension_needed_bookings)}")
        for extension_needed_booking in extension_needed_bookings:
            await self._create_extension_needed_task_instance(
                booking=extension_needed_booking,
                task_status=deal_need_extension_task_status,
                booking_settings=booking_settings,
            )

    async def _get_bookings(self, booking_settings: BookingSettings) -> tuple[list[Booking], list[Booking]]:
        """
        Получение списка сделок требующих и не требующих продления, которые не имеют задачи продления фиксации.
        """
        no_extension_needed_bookings: list[Booking] = await self.booking_repo.list(
            filters=dict(
                created__gte=datetime.now(tz=UTC) - timedelta(days=booking_settings.lifetime),
                created__lte=datetime.now(tz=UTC) - timedelta(days=booking_settings.extension_deadline),
                amocrm_status__group_status__name__in=BOOKING_UPDATE_FIXATION_STATUSES,
                fixation_expires__isnull=True,
                extension_number__isnull=True,
            ),
            prefetch_fields=["amocrm_status", "amocrm_status__group_status"],
        )

        extension_needed_bookings: list[Booking] = await self.booking_repo.list(
            filters=dict(
                created__gte=datetime.now(tz=UTC) - timedelta(days=booking_settings.extension_deadline),
                amocrm_status__group_status__name__in=BOOKING_UPDATE_FIXATION_STATUSES,
                fixation_expires__isnull=True,
                extension_number__isnull=True,
            ),
            prefetch_fields=["amocrm_status", "amocrm_status__group_status"],
        )

        return no_extension_needed_bookings, extension_needed_bookings

    async def _get_task_statuses(self) -> tuple[TaskStatus, TaskStatus]:
        """
        Получение статусов задач фиксаций.
        """

        no_extension_needed_task_status: TaskStatus = await self.task_status_repo.retrieve(
            filters=dict(slug=FixationExtensionSlug.NO_EXTENSION_NEEDED.value),
        )
        deal_need_extension_task_status: TaskStatus = await self.task_status_repo.retrieve(
            filters=dict(slug=FixationExtensionSlug.DEAL_NEED_EXTENSION.value),
        )
        if not no_extension_needed_task_status or not deal_need_extension_task_status:
            raise TaskStatusNotFoundError

        return no_extension_needed_task_status, deal_need_extension_task_status

    async def _create_no_extension_needed_task_instance(
        self,
        booking: Booking,
        task_status: TaskStatus,
        booking_settings: BookingSettings,
    ) -> None:
        """
        Кейс создания инстанса задачи фиксации, не требующей продления.
        """

        is_success_created: bool = await self._create_task_instance(booking=booking, task_status=task_status)
        if is_success_created:
            await self._update_instance_booking(booking=booking, booking_settings=booking_settings)

            # создаем отложенную задачу на изменение статуса задачи сделки фиксации, когда фиксация подходит к концу
            update_task_date = booking.fixation_expires - timedelta(
                booking_settings.extension_deadline
            )
            self.update_task_instance_status_task.apply_async(
                (booking.id, FixationExtensionSlug.DEAL_NEED_EXTENSION.value, self.__class__.__name__),
                eta=update_task_date,
            )

    async def _create_extension_needed_task_instance(
        self,
        booking: Booking,
        task_status: TaskStatus,
        booking_settings: BookingSettings,
    ) -> None:
        """
        Кейс создания инстанса задачи фиксации, требующей продления.
        """

        is_success_created: bool = await self._create_task_instance(booking=booking, task_status=task_status)
        if is_success_created:
            await self._update_instance_booking(booking=booking, booking_settings=booking_settings)

            # оставляем task_status, полученный по переданному status_slug
            # создаем отложенную задачу на изменение статуса по истечению дедлайна фиксации
            self.update_task_instance_status_task.apply_async(
                (booking.id, FixationExtensionSlug.CANT_EXTEND_DEAL_BY_DATE.value, self.__class__.__name__),
                eta=booking.fixation_expires,
            )
            # запускаем отложенные таски по отправке писем за N часов до окончания фиксации
            # и при окончании фиксации
            self.booking_fixation_notification_email_task.delay(booking_id=booking.id)

    async def _create_task_instance(
        self,
        booking: Booking,
        task_status: TaskStatus,
    ) -> bool:
        """
        Создание инстансов задач фиксаций.
        """
        if await self._is_task_not_in_fixation_chain(booking=booking):
            created_task: TaskInstance = await self.create_task(
                data=dict(
                    booking=booking,
                    status=task_status,
                    comment=None,
                )
            )
            self.logger.info(
                f"Задача {created_task} создана"
                f" для бронирования {booking}"
                f" со статусом {task_status}"
            )
            return True

    async def _update_instance_booking(self, booking: Booking, booking_settings: BookingSettings) -> None:
        """
        Добавление в сделки фиксаций количества продлений и даты окончания фиксации.
        """

        booking_data = dict(
            extension_number=booking_settings.max_extension_number,
            fixation_expires=booking.created + timedelta(days=booking_settings.lifetime),
        )
        await self.booking_repo.update(booking, booking_data)

    async def _is_task_not_in_fixation_chain(self, booking: Booking) -> bool:
        """
        Проверка, есть ли задача по данной сделке в цепочке фиксаций.
        """

        fixation_task_chain = await self.task_chain_repo.retrieve(filters=dict(name=self.FIXATION_TASK_CHAIN_NAME))
        task_instance: TaskInstance = await self.task_instance_repo.retrieve(
            filters=dict(booking=booking, status__tasks_chain=fixation_task_chain),
        )

        if task_instance:
            self.logger.info(f"Задача {task_instance} уже есть в цепочке {fixation_task_chain}")
            return False

        self.logger.info(f"Задачи в цепочке {fixation_task_chain} нет")
        return True
