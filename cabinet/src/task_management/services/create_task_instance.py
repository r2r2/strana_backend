import asyncio
from copy import copy
from typing import Any, Optional
from datetime import datetime, timedelta
from pytz import UTC

import structlog

from common.settings.repos import BookingSettingsRepo, BookingSettings
from src.booking.constants import BookingSubstages
from src.booking.exceptions import BookingNotFoundError
from src.booking.repos import Booking, BookingRepo
from src.booking.types import BookingORM
from src.task_management.constants import PaidBookingSlug, PackageOfDocumentsSlug, MeetingsSlug, FixationExtensionSlug
from src.task_management.entities import BaseTaskService
from src.task_management.exceptions import TaskChainNotFoundError, TaskStatusNotFoundError
from src.task_management.loggers import task_instance_logger
from src.task_management.repos import (
    TaskChain,
    TaskInstanceRepo,
    TaskStatusRepo,
    TaskChainRepo,
    TaskInstance,
    TaskStatus,
)


class CreateTaskInstanceService(BaseTaskService):
    """
    Сервис выбора кейса для создания экземпляра задания
    """

    def __init__(
        self,
        booking_repo: type[BookingRepo],
        task_instance_repo: type[TaskInstanceRepo],
        task_status_repo: type[TaskStatusRepo],
        task_chain_repo: type[TaskChainRepo],
        booking_settings_repo: type[BookingSettingsRepo],
        update_task_instance_status_task: Any,
        orm_class: Optional[BookingORM] = None,
        orm_config: Optional[dict[str, Any]] = None,
    ):
        self.booking_repo: BookingRepo = booking_repo()
        self.task_instance_repo: TaskInstanceRepo = task_instance_repo()
        self.task_status_repo: TaskStatusRepo = task_status_repo()
        self.task_chain_repo: TaskChainRepo = task_chain_repo()
        self.orm_class: Optional[type[BookingORM]] = orm_class
        self.orm_config: Optional[dict[str, Any]] = copy(orm_config)
        self.booking_settings_repo: BookingSettingsRepo = booking_settings_repo()
        self.update_task_instance_status_task = update_task_instance_status_task
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

        self.logger = structlog.get_logger(__name__)
        self.create_task = task_instance_logger(self.task_instance_repo.create, self, content="Создание задачи")

        # Слаги статусов
        self.paid_booking_statuses: type[PaidBookingSlug] = PaidBookingSlug
        self.package_of_docs_statuses: type[PackageOfDocumentsSlug] = PackageOfDocumentsSlug
        self.meetings_statuses: type[MeetingsSlug] = MeetingsSlug
        self.fixations_statuses: type[FixationExtensionSlug] = FixationExtensionSlug

        # Context for task, could be used in task creation
        self._task_context: Optional[dict[str, Any]] = None

    async def __call__(
        self,
        booking_ids: list[int],
        booking_created: bool = False,
        task_context: Optional[dict[str, Any]] = None,
    ) -> None:
        self._task_context: Optional[dict[str, Any]] = task_context if task_context else {}
        bookings: list[Booking] = await self.booking_repo.list(
            filters=dict(id__in=booking_ids),
            prefetch_fields=["amocrm_status"],
        )
        if not bookings:
            raise BookingNotFoundError

        task_chains: list[TaskChain] = await self.task_chain_repo.list(
            prefetch_fields=["booking_substage", "task_statuses"],
        )
        if not task_chains:
            raise TaskChainNotFoundError
        self.logger.info(
            f"Бронирования и цепочки задач получены:\n"
            f"Бронирования: {bookings}\n"
            f"Цепочки задач: {[t.name for t in task_chains]}\n"
        )

        for task_chain in task_chains:
            for booking in bookings:
                # Тут определяем, что нужно создать задачу
                if booking.amocrm_status and (booking.amocrm_status in task_chain.booking_substage):
                    self.logger.info(f"Бронирование {booking} подходит для цепочки задач {task_chain}")
                    asyncio.create_task(self.process_use_case(
                        booking=booking,
                        task_chain=task_chain,
                        booking_created=booking_created,
                    ))

    async def process_use_case(self, booking: Booking, task_chain: TaskChain, booking_created: bool) -> None:
        """
        Смотрим все статусы цепочки заданий,
        если статус соответствует статусам цепочки заданий - запускаем этот кейс
        Можно проверять на любой статус из цепочки заданий, главное запустить нужный кейс
        """
        for status in task_chain.task_statuses:
            if status.slug == self.paid_booking_statuses.START.value:
                self.logger.info(f"Кейс по платному бронированию для бронирования {booking}")
                await self.paid_booking_case(booking=booking, task_chain=task_chain)
                break
            elif status.slug == self.package_of_docs_statuses.START.value:
                self.logger.info(f"Кейс по загрузке документов для бронирования {booking}")
                await self.package_of_documents_case(booking=booking, task_chain=task_chain)
                break
            elif status.slug == self.meetings_statuses.SIGN_UP.value:
                self.logger.info(f"Кейс по встречам для бронирования {booking}")
                await self.meetings_case(booking=booking, task_chain=task_chain)
                break
            elif status.slug == self.fixations_statuses.NO_EXTENSION_NEEDED.value:
                self.logger.info(f"Кейс по продлению фиксации {booking}")
                await self.fixation_extension_case(
                    booking=booking,
                    task_chain=task_chain,
                    booking_created=booking_created,
                )
                break

    async def fixation_extension_case(self, booking: Booking, task_chain: TaskChain, booking_created: bool) -> None:
        """
        Создание задания для цепочки по Продления фиксации
        """
        task_status: TaskStatus = await self.get_task_status(
            filters=dict(slug=self.fixations_statuses.NO_EXTENSION_NEEDED.value),
        )

        if await self._is_task_not_in_this_chain(
            booking=booking,
            task_chain=task_chain,
        ):
            booking_settings: BookingSettings = await self.booking_settings_repo.list().first()
            if booking_created:
                fixation_expires = datetime.now(tz=UTC) + timedelta(days=booking_settings.lifetime)
            elif booking.fixation_expires:
                fixation_expires = booking.fixation_expires
            else:
                fixation_expires = None

            if fixation_expires:
                # обновляем поля в сделке для сохранения инфо о количестве продлений и дате окончания фиксации
                booking_data = dict(
                    extension_number=booking_settings.max_extension_number,
                    fixation_expires=fixation_expires,
                )
                await self.booking_repo.update(booking, booking_data)

                # если в цепочке нет задачи, создаем ее
                await self._create_task_instance(
                    booking=booking,
                    task_status=task_status,
                )

                # создаем отложенную задачу на изменение статуса задачи сделки фиксации, когда фиксация подходит к концу
                update_task_date = booking.fixation_expires - timedelta(booking_settings.extension_deadline)
                self.update_task_instance_status_task.apply_async(
                    (booking.id, self.fixations_statuses.DEAL_NEED_EXTENSION.value),
                    eta=update_task_date,
                )

    async def paid_booking_case(self, booking: Booking, task_chain: TaskChain) -> None:
        """
        Создание задания для цепочки по Платному бронированию
        """
        if booking.property:
            filters: dict[str: str] = dict(slug=self.paid_booking_statuses.RE_BOOKING.value)
        else:
            filters: dict[str: str] = dict(slug=self.paid_booking_statuses.START.value)
        task_status: TaskStatus = await self.get_task_status(filters=filters)

        if await self._is_task_not_in_this_chain(
            booking=booking,
            task_chain=task_chain,
        ):
            # Если в цепочке нет задачи, создаем ее
            await self._create_task_instance(
                booking=booking,
                task_status=task_status,
            )

    async def package_of_documents_case(self, booking: Booking, task_chain: TaskChain) -> None:
        """
        Создание задания для цепочки Загрузка документов
        """
        filters: dict[str: str] = dict(slug=self.package_of_docs_statuses.START.value)
        task_status: TaskStatus = await self.get_task_status(filters=filters)

        if await self._is_task_not_in_this_chain(
            booking=booking,
            task_chain=task_chain,
        ):
            # Если в цепочке нет задачи, создаем ее
            await self._create_task_instance(
                booking=booking,
                task_status=task_status,
            )

    async def meetings_case(self, booking: Booking, task_chain: TaskChain) -> None:
        """
        Создание задания для цепочки Встречи
        """
        if booking.amocrm_substage == BookingSubstages.MAKE_APPOINTMENT:
            filters: dict[str: str] = dict(slug=self.meetings_statuses.AWAITING_CONFIRMATION.value)

        elif booking.amocrm_substage == BookingSubstages.MEETING:
            if self._task_context.get("meeting_new_date"):
                filters: dict[str: str] = dict(slug=self.meetings_statuses.CONFIRMED_RESCHEDULED.value)
            else:
                filters: dict[str: str] = dict(slug=self.meetings_statuses.CONFIRMED.value)

        else:
            task_status: str = self._task_context.get("task_status", self.meetings_statuses.SIGN_UP.value)
            filters: dict[str: str] = dict(slug=task_status)

        task_status: TaskStatus = await self.get_task_status(filters=filters)

        if await self._is_task_not_in_this_chain(
            booking=booking,
            task_chain=task_chain,
        ):
            # Если в цепочке нет задачи, создаем ее
            await self._create_task_instance(
                booking=booking,
                task_status=task_status,
            )

    async def get_task_status(self, filters: dict[str, Any]) -> TaskStatus:
        """
        Получение статуса задачи
        """
        task_status: TaskStatus = await self.task_status_repo.retrieve(
            filters=filters,
        )
        if not task_status:
            raise TaskStatusNotFoundError
        self.logger.info(f"Статус задачи {task_status}")
        return task_status

    async def _create_task_instance(
        self,
        booking: Booking,
        task_status: TaskStatus,
        comment: Optional[str] = None,
    ) -> None:
        """
        Создание задания
        """
        task: TaskInstance = await self.create_task(
            data=dict(
                booking=booking,
                status=task_status,
                comment=comment,
            )
        )
        self.logger.info(
            f"Задача {task} создана"
            f" для бронирования {booking}"
            f" со статусом {task_status}"
        )

    async def _is_task_not_in_this_chain(
        self,
        booking: Booking,
        task_chain: TaskChain,
    ) -> bool:
        """
        Проверка, есть ли задача в цепочке
        """
        task_instance: TaskInstance = await self.task_instance_repo.retrieve(
            filters=dict(booking=booking, status__tasks_chain=task_chain),
        )
        # If current TaskChain already have associated TaskInstance, do not need to create new one
        if task_instance:
            self.logger.info(f"Задача {task_instance} уже есть в цепочке {task_chain}")
            return False
        self.logger.info(f"Задачи в цепочке {task_chain} нет")
        return True
