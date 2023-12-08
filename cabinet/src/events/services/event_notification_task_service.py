import structlog
from datetime import datetime, timedelta
from pytz import UTC
from typing import Any

from config import celery_config
from src.users.repos import User
from src.notifications.repos import EventsSmsNotification, EventsSmsNotificationType

from ..entities import BaseEventCase
from ..repos import Event
from .get_event_sms_notification_service import GetEventNotificationTaskService


class EventNotificationTaskService(BaseEventCase):
    """
    Сервис непосредственного создания eta задач оповещения брокеров о мероприятиях до их наступления и после их
    окончания (на случай, когда периодическая задача создания eta уже ранее была выполнена в данный временной период).
    """

    _day_hours = 24

    def __init__(
        self,
        get_event_sms_notification_service: GetEventNotificationTaskService,
        sending_sms_to_broker_on_event_task: Any,
    ) -> None:
        self.get_event_sms_notification_service: GetEventNotificationTaskService = get_event_sms_notification_service
        self.sending_sms_to_broker_on_event_task = sending_sms_to_broker_on_event_task

        self.logger: structlog.BoundLogger = structlog.get_logger(self.__class__.__name__)

    async def __call__(
        self,
        event: Event,
        user: User,
        sms_event_type: Any,
    ) -> None:
        is_need_to_create_eta_task: bool = self._is_need_to_create_eta_task(
            event=event,
            sms_event_type=sms_event_type,
        )
        if not is_need_to_create_eta_task:
            self.logger.info(
                f"Для агента [{user.id=}] не нужно создавать eta задачу на отправку смс "
                f"по мероприятию [{event.id=}] о событии [{sms_event_type}] - задача будет через периодическую задачу",
            )
            return

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

        if sms_event_type == EventsSmsNotificationType.BEFORE:
            task_delay_date = event.time_to_send_sms_before
        else:
            task_delay_date = event.time_to_send_sms_after

        if task_delay_date:
            task_data = (event.id, user.id, event_sms_notification_result.sms_template.sms_event_slug)
            self.sending_sms_to_broker_on_event_task.apply_async(
                task_data,
                eta=task_delay_date,
                queue="scheduled"
            )
            self.logger.info(
                f"Для агента [{user.id=}] создана eta задача на отправку смс "
                f"по мероприятию [{event.id=}] о событии [{sms_event_type}]",
            )

    def _is_need_to_create_eta_task(
        self,
        event: Event,
        sms_event_type: Any,
    ) -> bool:
        """
        Проверка, что требуется создать отложенную eta задачу
        (на случай, когда периодическая задача создания eta уже ранее была выполнена в данный временной период
        или, если событие не попадает в новую периодическую задачу).
        """

        datetime_now = datetime.now(tz=UTC)
        time_now = datetime_now.time()
        date_now = datetime_now.date()

        # поля для проверки условий по времени периода до запуска периодической задачи в этот временной период
        time_before = datetime.strptime("00:00", '%H:%S').time()
        time_after = datetime.strptime("02:00", '%H:%M').time()   # 02:00 - время запуска периодической задачи

        # не выполнять дальнейшие проверки, если задача запускается не раз в сутки
        periodic_eta_timeout_hours = celery_config.get("periodic_eta_timeout_hours", 24)
        if periodic_eta_timeout_hours != self._day_hours:
            return False

        if sms_event_type == EventsSmsNotificationType.BEFORE:
            datetime_to_send_sms: datetime = event.time_to_send_sms_before
        else:
            datetime_to_send_sms: datetime = event.time_to_send_sms_after

        if not datetime_to_send_sms or datetime_to_send_sms < datetime_now:
            return False

        # проверка условия, когда агент добавлен на мероприятие до запуска периодической задачи
        if time_before <= time_now <= time_after:
            if time_before <= datetime_to_send_sms.time() <= time_after and datetime_to_send_sms.date() == date_now:
                return True

        # # проверка условия, когда агент добавлен на мероприятие после запуска периодической задачи
        else:
            if datetime_to_send_sms.date() == date_now:
                return True
            elif (
                (datetime_to_send_sms - timedelta(hours=periodic_eta_timeout_hours)).date() == date_now
                and time_before <= datetime_to_send_sms.time() <= time_after
            ):
                return True

        return False
