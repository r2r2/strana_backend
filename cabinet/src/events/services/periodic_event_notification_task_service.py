import structlog
from typing import Any, Optional
from copy import copy
from datetime import datetime, timedelta
from pytz import UTC
from tortoise import Tortoise

from config import celery_config
from src.events.entities import BaseEventCase
from src.events.repos import EventRepo, Event
from src.notifications.repos import EventsSmsNotification, EventsSmsNotificationType

from .get_event_sms_notification_service import GetEventNotificationTaskService


class PeriodicEventNotificationTaskService(BaseEventCase):
    """
    Периодический сервис создание отложенных eta задач на уведомление агентов о начале и окончании мероприятий.
    """

    def __init__(
        self,
        event_repo: type[EventRepo],
        get_event_sms_notification_service: GetEventNotificationTaskService,
        sending_sms_to_broker_on_event_task: Any,
        orm_class: Optional[Tortoise] = None,
        orm_config: Optional[dict[str, Any]] = None,
    ):
        self.event_repo: EventRepo = event_repo()
        self.get_event_sms_notification_service: GetEventNotificationTaskService = get_event_sms_notification_service
        self.sending_sms_to_broker_on_event_task = sending_sms_to_broker_on_event_task
        self.orm_class: Optional[type[Tortoise]] = orm_class
        self.orm_config: Optional[dict[str, Any]] = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

        self.logger: structlog.BoundLogger = structlog.get_logger(self.__class__.__name__)

    async def __call__(self) -> None:
        # добавление в eta очередь задачи для уведомления агентов о начале мероприятий
        starting_event_filters = dict(
            time_to_send_sms_before__gte=datetime.now(UTC),
            time_to_send_sms_before__lte=(
                datetime.now(UTC)
                + timedelta(hours=celery_config.get("periodic_eta_timeout_hours", 24))
            ),
            is_active=True,
        )
        starting_events: list[Event] = await self.event_repo.list(
            filters=starting_event_filters,
            prefetch_fields=["participants", "participants__agent"],
        )
        self.logger.info(
            f"Мероприятия, по которым в течении суток нужно отправить смс о начале, в количестве - "
            f"{len(starting_events) if starting_events else 0} шт"
        )
        for event in starting_events:
            await self._process_event(
                event=event,
                sms_event_type=EventsSmsNotificationType.BEFORE,
            )

        # добавление в eta очередь задачи для уведомления агентов об окончании мероприятий
        ending_event_filters = dict(
            time_to_send_sms_after__gte=datetime.now(UTC),
            time_to_send_sms_after__lte=(
                datetime.now(UTC) + timedelta(hours=celery_config.get("periodic_eta_timeout_hours", 24))
            ),
            is_active=True,
        )
        ending_events: list[Event] = await self.event_repo.list(
            filters=ending_event_filters,
            prefetch_fields=["participants", "participants__agent"],
        )
        self.logger.info(
            f"Мероприятия, по которым в течении суток нужно отправить смс об окончании, в количестве - "
            f"{len(ending_events) if ending_events else 0} шт"
        )
        for event in ending_events:
            await self._process_event(
                event=event,
                sms_event_type=EventsSmsNotificationType.AFTER,
            )

    async def _process_event(
        self,
        event: Event,
        sms_event_type: Any,
    ) -> None:
        event_sms_notification_result: EventsSmsNotification = await self.get_event_sms_notification_service(
            event=event,
            sms_event_type=sms_event_type,
        )
        if not event_sms_notification_result:
            self.logger.error(
                f"Для мероприятия [{event.id=}] не найден шаблон смс для уведомления агентов о событии "
                f"[{sms_event_type}]",
            )
            return

        self.logger.info(
            f"Для мероприятия [{event.id=}] найдено участников, в количестве - "
            f"{len(event.participants) if event.participants else 0} шт",
        )
        for participant in event.participants:
            task_data = (event.id, participant.agent.id, event_sms_notification_result.sms_template.sms_event_slug)

            if sms_event_type == EventsSmsNotificationType.BEFORE:
                task_delay_date = event.time_to_send_sms_before
            else:
                task_delay_date = event.time_to_send_sms_after

            self.sending_sms_to_broker_on_event_task.apply_async(
                task_data,
                eta=task_delay_date,
                queue="scheduled",
            )
            self.logger.info(
                f"Для агента [{participant.agent}] создана eta задача на отправку смс "
                f"по мероприятию [{event.id=}] о событии [{sms_event_type}]",
            )
