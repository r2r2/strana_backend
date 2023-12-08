import structlog

from src.events.entities import BaseEventCase
from src.events.repos import Event, EventType
from src.notifications.repos import EventsSmsNotification, EventsSmsNotificationRepo, EventsSmsNotificationType


class GetEventNotificationTaskService(BaseEventCase):
    """
    Сервис запуска задачи оповещения брокеров о мероприятиях до их наступления и после их окончания.
    """

    def __init__(
        self,
        event_sms_notification_repo: type[EventsSmsNotificationRepo],
    ):
        self.event_sms_notification_repo: EventsSmsNotificationRepo = event_sms_notification_repo()

        self.logger: structlog.BoundLogger = structlog.get_logger(self.__class__.__name__)

    async def __call__(
        self,
        event: Event,
        sms_event_type: EventsSmsNotificationType,
    ) -> EventsSmsNotification:
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

        if event_sms_notification_result and event_sms_notification_result.sms_template:
            return event_sms_notification_result
