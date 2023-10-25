import datetime
from typing import Any, Type

from src.users.repos import User
from src.notifications.repos import EventsSmsNotificationRepo, EventsSmsNotification, EventsSmsNotificationType

from ..entities import BaseEventCase
from ..repos import Event, EventType


class GetEventNotificationTaskService(BaseEventCase):
    """
    Сервис запуска задачи оповещения брокеров о мероприятиях до их наступления и после их окончания.
    """

    def __init__(
        self,
        event_sms_notification_repo: Type[EventsSmsNotificationRepo],
        sending_sms_to_broker_on_event_task: Any,
    ) -> None:
        self.event_sms_notification_repo: EventsSmsNotificationRepo = event_sms_notification_repo()
        self.sending_sms_to_broker_on_event_task = sending_sms_to_broker_on_event_task

    async def __call__(
        self,
        event: Event,
        user: User,
        sms_event_type: Any,
    ) -> None:
        if event.type == EventType.ONLINE:
            event_sms_notification_result: EventsSmsNotification = (
                await self.event_sms_notification_repo.retrieve(
                    filters=dict(
                        only_for_online=True,
                        sms_event_type=sms_event_type,
                    ),
                    prefetch_fields=["sms_template"],
                )
            )
        else:
            offline_events_sms_notification: list[EventsSmsNotification] = (
                await self.event_sms_notification_repo.list(
                    filters=dict(
                        only_for_online=False,
                        sms_event_type=sms_event_type,
                    ),
                    prefetch_fields=["sms_template", "cities"],
                )
            )

            event_sms_notification_result = None
            for event_sms_notification in offline_events_sms_notification:
                event_notification_cities: list[int] = [city.id for city in event_sms_notification.cities]
                if event.city_id in event_notification_cities:
                    event_sms_notification_result = event_sms_notification
                    break

        if (
            event_sms_notification_result
            and event_sms_notification_result.sms_template
            and event_sms_notification_result.days
        ):
            task_data = (event.id, user.id, event_sms_notification_result.sms_template.sms_event_slug)

            if sms_event_type == EventsSmsNotificationType.BEFORE:
                task_delay_date = event.meeting_date_start - datetime.timedelta(
                    days=event_sms_notification_result.days
                )
            else:
                task_delay_date = event.meeting_date_start + datetime.timedelta(
                    days=event_sms_notification_result.days
                )

            self.sending_sms_to_broker_on_event_task.apply_async(
                task_data,
                eta=task_delay_date,
            )
