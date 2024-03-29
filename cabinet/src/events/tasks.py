from asyncio import get_event_loop
from typing import Any

from tortoise import Tortoise

from common import messages
from config import celery, tortoise_config
from src.notifications import repos as notifications_repos
from src.notifications import services as notification_services
from src.users import repos as users_repos
from src.events import repos as events_repos
from src.events.services import (
    SendingSmsToBrokerOnEventService,
    PeriodicEventNotificationTaskService,
    GetEventNotificationTaskService,
)


@celery.app.task
def sending_sms_to_broker_on_event_task(event_id: int, broker_id: int, sms_event_slug: str) -> None:
    """
    Отложенная задача на отправку смс уведомлений брокерам, записанным на мероприятие.
    """

    get_sms_template_service: notification_services.GetSmsTemplateService = notification_services.GetSmsTemplateService(
        sms_template_repo=notifications_repos.SmsTemplateRepo,
    )
    resources: dict[str, Any] = dict(
        event_repo=events_repos.EventRepo,
        event_participant_repo=events_repos.EventParticipantRepo,
        user_repo=users_repos.UserRepo,
        sms_class=messages.SmsService,
        get_sms_template_service=get_sms_template_service,
        orm_class=Tortoise,
        orm_config=tortoise_config,
    )
    sending_sms_to_broker_on_event_service: SendingSmsToBrokerOnEventService = SendingSmsToBrokerOnEventService(
        **resources
    )
    loop: Any = get_event_loop()
    loop.run_until_complete(celery.sentry_catch(celery.init_orm(sending_sms_to_broker_on_event_service))(
        event_id=event_id,
        broker_id=broker_id,
        sms_event_slug=sms_event_slug,
    ))


@celery.app.task
def periodic_event_notification_task() -> None:
    """
    Периодическая задача на создание отложенных eta задач на уведомление агентов о начале и окончании мероприятий.
    """

    resources: dict[str, Any] = dict(
        event_sms_notification_repo=notifications_repos.EventsSmsNotificationRepo,
    )
    get_event_sms_notification_service: GetEventNotificationTaskService = GetEventNotificationTaskService(
        **resources
    )
    resources: dict[str, Any] = dict(
        event_repo=events_repos.EventRepo,
        get_event_sms_notification_service=get_event_sms_notification_service,
        sending_sms_to_broker_on_event_task=sending_sms_to_broker_on_event_task,
        orm_class=Tortoise,
        orm_config=tortoise_config,
    )
    periodic_event_notification_task_service: PeriodicEventNotificationTaskService = \
        PeriodicEventNotificationTaskService(
            **resources
        )
    loop: Any = get_event_loop()
    loop.run_until_complete(celery.sentry_catch(celery.init_orm(periodic_event_notification_task_service))())
