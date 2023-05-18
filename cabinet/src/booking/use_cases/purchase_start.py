from datetime import datetime
from typing import Any, Optional, Type

from common.amocrm import AmoCRM
from common.amocrm.types import AmoTask
from pytz import UTC
from src.booking.loggers.wrappers import booking_changes_logger

from ..constants import OnlinePurchaseStatuses, OnlinePurchaseSteps
from ..decorators import logged_action
from ..entities import BaseBookingCase
from ..exceptions import BookingNotFoundError, BookingWrongStepError
from ..mixins import BookingLogMixin
from ..repos import Booking, BookingRepo
from ..services import HistoryService, NotificationService


class PurchaseStartCase(BaseBookingCase, BookingLogMixin):
    """
    Переход пользователя к онлайн-покупке
    """

    purchase_tag = "онлайн-покупка"
    text_of_task_to_be_completed = "Уточни что клиент хочет делать дальше?"
    task_complete_result_text = "онлайн-покупка"
    _notification_template = "src/booking/templates/notifications/purchase_start.json"
    _history_template = "src/booking/templates/history/purchase_start.txt"

    def __init__(
        self,
        create_booking_log_task: Any,
        backend_config: dict[str, Any],
        booking_repo: Type[BookingRepo],
        amocrm_class: Type[AmoCRM],
        history_service: HistoryService,
        notification_service: NotificationService,
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()

        self.amocrm_class: Type[AmoCRM] = amocrm_class
        self.create_booking_log_task: Any = create_booking_log_task

        self.connection_options: dict[str, Any] = dict(
            user=backend_config["db_user"],
            host=backend_config["db_host"],
            port=backend_config["db_port"],
            database=backend_config["db_name"],
            password=backend_config["db_password"],
        )

        self._history_service = history_service
        self._notification_service = notification_service
        self.booking_update = booking_changes_logger(self.booking_repo.update, self, content="Переход пользователя")

    async def __call__(self, user_id: int, booking_id: int) -> Booking:
        filters: dict[str, Any] = dict(id=booking_id, user_id=user_id, active=True)
        booking: Booking = await self.booking_repo.retrieve(
            filters=filters,
            related_fields=["project", "property", "floor", "building", "ddu"],
            prefetch_fields=["ddu__participants"],
        )
        if not booking:
            raise BookingNotFoundError

        previous_online_purchase_step = booking.online_purchase_step()
        self._check_step_requirements(booking)

        tags: list[str] = booking.tags if booking.tags else []
        tags.append(self.purchase_tag)
        data: dict[str, Any] = dict(
            tags=tags,
            amocrm_purchase_status=OnlinePurchaseStatuses.STARTED,
            online_purchase_started=True,
            purchase_start_datetime=datetime.now(tz=UTC),
        )

        booking = await self.booking_update(booking=booking, data=data)
        await self._amocrm_hook(booking)

        await self._history_service.execute(
            booking=booking,
            previous_online_purchase_step=previous_online_purchase_step,
            template=self._history_template,
        )

        await self._notification_service(
            booking=booking,
            previous_online_purchase_step=previous_online_purchase_step,
            template=self._notification_template,
        )

        return booking

    # @logged_action(content="НАЧАЛО ОНЛАЙН ПОКУПКИ | AMOCRM")
    async def _amocrm_hook(self, booking: Booking) -> int:
        """amocrm hook"""
        amocrm: AmoCRM
        async with await self.amocrm_class() as amocrm:
            # Ставим тег "онлайн-покупка" в сделке
            # Меняем значение свойства "статус онлайн-покупки" на "приступил к онлайн-покупке"
            # Заполняем поле "дата и время начала онлайн-покупки"
            data: list[Any] = await amocrm.update_lead(
                lead_id=booking.amocrm_id,
                tags=booking.tags,
                online_purchase_status=booking.amocrm_purchase_status,
                online_purchase_start_datetime=int(booking.purchase_start_datetime.timestamp()),
            )
            lead_id: int = data[0]["id"]

            # Завершаем задачу "Уточни что клиент хочет делать дальше?"
            # с результатом "онлайн-покупка"
            tasks = await amocrm.fetch_booking_tasks(booking_id=lead_id)
            task: Optional[AmoTask] = next(
                filter(lambda _task: _task["text"] == self.text_of_task_to_be_completed, tasks),
                None,
            )

            if task is not None:
                await amocrm.complete_task(
                    task_id=task["id"], result=self.task_complete_result_text
                )

        return lead_id

    @classmethod
    def _check_step_requirements(cls, booking: Booking) -> None:
        """Проверка текущего шага."""
        if booking.online_purchase_step() != OnlinePurchaseSteps.ONLINE_PURCHASE_START:
            raise BookingWrongStepError
