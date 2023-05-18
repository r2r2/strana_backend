from copy import copy
from typing import Any, Optional

from common.sensei import SenseiAPI
from src.booking.exceptions import BookingNotFoundError
from src.booking.repos import Booking, BookingRepo
from src.booking.types import BookingORM
from src.task_management.constants import PaidBookingSlug, PackageOfDocumentsSlug
from src.task_management.entities import BaseTaskService
from src.task_management.exceptions import TaskChainNotFoundError, TaskStatusNotFoundError
from src.task_management.repos import (TaskChain, TaskInstanceRepo,
                                       TaskStatusRepo, TaskChainRepo, TaskInstance, TaskStatus)


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
        orm_class: Optional[BookingORM] = None,
        orm_config: Optional[dict[str, Any]] = None,
    ):
        self.booking_repo: BookingRepo = booking_repo()
        self.task_instance_repo: TaskInstanceRepo = task_instance_repo()
        self.task_status_repo: TaskStatusRepo = task_status_repo()
        self.task_chain_repo: TaskChainRepo = task_chain_repo()
        self.orm_class: Optional[type[BookingORM]] = orm_class
        self.orm_config: Optional[dict[str, Any]] = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

        self.sensei: type[SenseiAPI] = SenseiAPI

        # Слаги статусов
        self.paid_booking_statuses: type[PaidBookingSlug] = PaidBookingSlug
        self.package_of_docs_statuses: type[PackageOfDocumentsSlug] = PackageOfDocumentsSlug

    async def __call__(self, booking_ids: list[int]) -> None:
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

        for task_chain in task_chains:
            for booking in bookings:
                # Тут определяем, что нужно создать задачу
                if booking.amocrm_status and (booking.amocrm_status in task_chain.booking_substage):
                    await self.process_use_case(
                        booking=booking,
                        task_chain=task_chain,
                    )

    async def process_use_case(self, booking: Booking, task_chain: TaskChain) -> None:
        """
        Смотрим все статусы цепочки заданий,
        если статус соответствует статусам цепочки заданий - запускаем этот кейс
        """
        for status in task_chain.task_statuses:
            if status.slug == self.paid_booking_statuses.START.value:
                await self.paid_booking_case(booking=booking, task_chain=task_chain)
                break
            elif status.slug == self.package_of_docs_statuses.START.value:
                await self.package_of_documents_case(booking=booking, task_chain=task_chain)
                break

    async def paid_booking_case(self, booking: Booking, task_chain: TaskChain) -> None:
        """
        Создание задания для цепочки по Платному бронированию
        """
        if booking.property:
            filters: dict[str: str] = dict(slug=self.paid_booking_statuses.RE_BOOKING.value)
        else:
            filters: dict[str: str] = dict(slug=self.paid_booking_statuses.START.value)
        task_status: TaskStatus = await self.task_status_repo.retrieve(
            filters=filters,
        )
        if not task_status:
            raise TaskStatusNotFoundError

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
        task_status: TaskStatus = await self.task_status_repo.retrieve(
            filters=filters,
        )
        if not task_status:
            raise TaskStatusNotFoundError

        if await self._is_task_not_in_this_chain(
            booking=booking,
            task_chain=task_chain,
        ):
            # Если в цепочке нет задачи, создаем ее
            await self._create_task_instance(
                booking=booking,
                task_status=task_status,
            )

    async def _create_task_instance(
        self,
        booking: Booking,
        task_status: TaskStatus,
        comment: Optional[str] = None,
    ) -> None:
        """
        Создание задания
        """
        await self.task_instance_repo.create(
            data=dict(
                booking=booking,
                status=task_status,
                comment=comment,
                sensei_pid=self.sensei.SENSEI_PID,
            )
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
            return False
        return True
