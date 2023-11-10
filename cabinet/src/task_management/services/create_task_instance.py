import asyncio
from copy import copy
from datetime import datetime, timedelta
from typing import Any, Optional, Union, Callable

import structlog
from pytz import UTC
from tortoise.transactions import atomic

from common.settings.repos import BookingSettingsRepo, BookingSettings
from src.booking.constants import BookingSubstages
from src.booking.exceptions import BookingNotFoundError
from src.booking.repos import Booking, BookingRepo
from src.booking.types import BookingORM
from src.booking.loggers import booking_changes_logger
from src.task_management.constants import (
    PaidBookingSlug,
    PackageOfDocumentsSlug,
    MeetingsSlug,
    FixationExtensionSlug,
    OnlineBookingSlug,
    FastBookingSlug,
    FreeBookingSlug,
)
from src.task_management.dto import CreateTaskDTO
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
from src.task_management.utils import get_statuses_before_paid_booking


class CreateTaskInstanceService(BaseTaskService):
    """
    Сервис выбора кейса для создания экземпляра задания
    """
    # Context for task, could be used in task creation
    _task_context: CreateTaskDTO

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
        self.booking_update: Callable = booking_changes_logger(
            self.booking_repo.update, self, content="Обновление бронирования при создании задачи фиксации",
        )

        # Слаги статусов
        self.paid_booking_statuses: type[PaidBookingSlug] = PaidBookingSlug
        self.package_of_docs_statuses: type[PackageOfDocumentsSlug] = PackageOfDocumentsSlug
        self.meetings_statuses: type[MeetingsSlug] = MeetingsSlug
        self.fixations_statuses: type[FixationExtensionSlug] = FixationExtensionSlug
        self.online_booking_statuses: type[OnlineBookingSlug] = OnlineBookingSlug
        self.fast_booking_statuses: type[FastBookingSlug] = FastBookingSlug
        self.free_booking_statuses: type[FreeBookingSlug] = FreeBookingSlug

        self.status_to_case_mapping: dict[str, Callable[..., Any]] = {
            self.paid_booking_statuses.START.value: self.paid_booking_case,
            self.package_of_docs_statuses.START.value: self.package_of_documents_case,
            self.meetings_statuses.SIGN_UP.value: self.meetings_case,
            self.fixations_statuses.NO_EXTENSION_NEEDED.value: self.fixation_extension_case,
            self.online_booking_statuses.ACCEPT_OFFER.value: self.online_booking_case,
            self.fast_booking_statuses.ACCEPT_OFFER.value: self.fast_booking_case,
            self.free_booking_statuses.EXTEND.value: self.free_booking_case,
        }

    async def __call__(
        self,
        booking_ids: Union[list[int], int],
        task_context: CreateTaskDTO | None = None,
    ) -> None:
        self._task_context: CreateTaskDTO = task_context if task_context else CreateTaskDTO()
        if isinstance(booking_ids, int):
            booking_ids: list[int] = [booking_ids]

        bookings: list[Booking] = await self.booking_repo.list(
            filters=dict(id__in=set(booking_ids)),
            related_fields=["booking_source"],
            prefetch_fields=["amocrm_status"],
        )
        if not bookings:
            raise BookingNotFoundError

        task_chains: list[TaskChain] = await self.task_chain_repo.list(
            prefetch_fields=[
                "booking_substage",
                "task_statuses",
                "booking_source",
            ],
        )
        if not task_chains:
            raise TaskChainNotFoundError
        self.logger.info(
            f"\nБронирования и цепочки задач получены:\n"
            f"Бронирования: {bookings}\n"
            f"Цепочки задач: {[t.name for t in task_chains]}\n"
        )
        tasks = [
            self._process_booking_with_task_chains(bookings, task_chain)
            for task_chain in task_chains
        ]
        await asyncio.gather(*tasks)

    async def _process_booking_with_task_chains(self, bookings: list[Booking], task_chain: TaskChain) -> None:
        for booking in bookings:
            # Тут определяем, что нужно создать задачу
            if await self._check_if_need_to_create_task(booking=booking, task_chain=task_chain):
                self.logger.info(f"Бронирование #{booking} подходит для цепочки задач [{task_chain}]")

                await self.process_use_case(booking=booking, task_chain=task_chain)

    async def _check_if_need_to_create_task(self, booking: Booking, task_chain: TaskChain) -> bool:
        """
        Проверка, нужно ли создавать задачу
        return True -> нужно создать задачу
        return False -> не нужно создавать задачу
        """
        if not booking.amocrm_status or booking.amocrm_status not in task_chain.booking_substage:
            # Статус сделки не входит в статусы цепочки задач для создания задачи
            return False

        if not task_chain.booking_source:
            # Если в цепочке задач не указаны источники бронирования, то создаем задачу
            return True

        if booking.booking_source in task_chain.booking_source:
            # Если источник бронирования сделки входит в источники цепочки задач, то создаем задачу
            return True

        # Источник бронирования сделки не входит в источники цепочки задач, не создаем задачу
        return False

    async def process_use_case(self, booking: Booking, task_chain: TaskChain) -> None:
        """
        Смотрим все статусы цепочки заданий,
        если статус соответствует статусам цепочки заданий - запускаем этот кейс
        Можно проверять на любой статус из цепочки заданий, главное запустить нужный кейс
        """
        for status in task_chain.task_statuses:
            case_method = self.status_to_case_mapping.get(status.slug)
            if case_method:
                self.logger.info(f"Кейс для статуса [{status.name}] для бронирования #{booking}")
                await case_method(booking=booking, task_chain=task_chain)
                break

    async def fixation_extension_case(self, booking: Booking, task_chain: TaskChain) -> None:
        """
        Создание задания для цепочки по Продления фиксации
        """
        task_status: TaskStatus = await self.get_task_status(
            filters=dict(slug=self.fixations_statuses.NO_EXTENSION_NEEDED.value),
        )

        booking_settings: BookingSettings = await self.booking_settings_repo.list().first()
        if self._task_context.booking_created:
            fixation_expires = datetime.now(tz=UTC) + timedelta(days=booking_settings.lifetime)
        elif booking.fixation_expires:
            fixation_expires = booking.fixation_expires
        else:
            fixation_expires = None

        if not fixation_expires:
            return

        # обновляем поля в сделке для сохранения инфо о количестве продлений и дате окончания фиксации
        booking_data = dict(
            extension_number=booking_settings.max_extension_number,
            fixation_expires=fixation_expires,
        )
        await self.booking_update(booking=booking, data=booking_data)

        if booking.extension_number and booking.fixation_expires:
            task_created: bool = await self.create_task_instance(
                booking=booking,
                task_status=task_status,
                task_chain=task_chain,
            )
            if task_created:
                # создаем отложенную задачу на изменение статуса задачи сделки фиксации,
                # когда фиксация подходит к концу
                update_task_date = booking.fixation_expires - timedelta(days=booking_settings.extension_deadline)
                self.update_task_instance_status_task.apply_async(
                    (booking.id, self.fixations_statuses.DEAL_NEED_EXTENSION.value, self.__class__.__name__),
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

        await self.create_task_instance(
            booking=booking,
            task_status=task_status,
            task_chain=task_chain,
        )

    async def package_of_documents_case(self, booking: Booking, task_chain: TaskChain) -> None:
        """
        Создание задания для цепочки Загрузка документов
        """
        filters: dict[str: str] = dict(slug=self.package_of_docs_statuses.START.value)
        task_status: TaskStatus = await self.get_task_status(filters=filters)
        await self.create_task_instance(
            booking=booking,
            task_status=task_status,
            task_chain=task_chain,
        )

    async def meetings_case(self, booking: Booking, task_chain: TaskChain) -> None:
        """
        Создание задания для цепочки Встречи
        """
        if booking.amocrm_substage == BookingSubstages.MAKE_APPOINTMENT:
            filters: dict[str: str] = dict(slug=self.meetings_statuses.AWAITING_CONFIRMATION.value)

        elif booking.amocrm_substage == BookingSubstages.MEETING:
            if self._task_context.meeting_new_date:
                filters: dict[str: str] = dict(slug=self.meetings_statuses.CONFIRMED_RESCHEDULED.value)
            else:
                filters: dict[str: str] = dict(slug=self.meetings_statuses.CONFIRMED.value)

        else:
            task_status: str = self._task_context.status_slug or self.meetings_statuses.SIGN_UP.value
            filters: dict[str: str] = dict(slug=task_status)

        task_status: TaskStatus = await self.get_task_status(filters=filters)

        await self.create_task_instance(
            booking=booking,
            task_status=task_status,
            task_chain=task_chain,
        )

    async def online_booking_case(self, booking: Booking, task_chain: TaskChain) -> None:
        """
        Создание задания для цепочки Онлайн бронирования
        """
        status_valid: bool = booking.amocrm_status.id in await get_statuses_before_paid_booking()
        self.logger.info(
            f"Статус сделки [{booking.amocrm_status.id}] in [await get_statuses_before_paid_booking()]: {status_valid}"
        )
        if status_valid:
            # Если статус сделки входит в статусы до Платного бронирования, то создаем задачу
            filters: dict[str: str] = dict(slug=self.online_booking_statuses.ACCEPT_OFFER.value)
            task_status: TaskStatus = await self.get_task_status(filters=filters)
            await self.create_task_instance(
                booking=booking,
                task_status=task_status,
                task_chain=task_chain,
            )

    async def fast_booking_case(self, booking: Booking, task_chain: TaskChain) -> None:
        """
        Создание задания для цепочки Быстрого бронирования
        """
        filters: dict[str: str] = dict(slug=self.fast_booking_statuses.ACCEPT_OFFER.value)
        task_status: TaskStatus = await self.get_task_status(filters=filters)
        await self.create_task_instance(
            booking=booking,
            task_status=task_status,
            task_chain=task_chain,
        )

    async def free_booking_case(self, booking: Booking, task_chain: TaskChain) -> None:
        filters: dict[str, Any] = dict(slug=self.free_booking_statuses.EXTEND.value)
        task_status: TaskStatus = await self.get_task_status(filters=filters)
        await self.create_task_instance(
            booking=booking,
            task_status=task_status,
            task_chain=task_chain,
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
        self.logger.info(f"Статус задачи [{task_status}]")
        return task_status

    @atomic(connection_name="cabinet")
    async def create_task_instance(
        self,
        booking: Booking,
        task_status: TaskStatus,
        task_chain: TaskChain,
    ) -> bool:
        if await self.__is_task_not_in_this_chain(
            booking=booking,
            task_chain=task_chain,
        ):
            # Если в цепочке нет задачи, создаем ее
            await self.__create_task_instance(
                booking=booking,
                task_status=task_status,
            )
            return True
        return False

    async def __create_task_instance(
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
                current_step=task_status.slug,
                is_main=self._task_context.is_main,
            )
        )
        self.logger.info(
            f"Задача [{task}] создана"
            f" для бронирования #{booking}"
            f" со статусом [{task_status}]"
        )

    async def __is_task_not_in_this_chain(
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
            self.logger.info(f"Задача [{task_instance}] уже есть в цепочке [{task_chain}]. Не создаем новую задачу")
            return False
        self.logger.info(f"Задачи в цепочке [{task_chain}] нет. Создаем новую задачу")
        return True
