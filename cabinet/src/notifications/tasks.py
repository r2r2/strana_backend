from asyncio import get_event_loop
from typing import Any

from common import email, messages
from common.settings.repos import BookingSettingsRepo
from config import celery, tortoise_config, logs_config
from tortoise import Tortoise
from common.email.repos import LogEmailRepo
from common.messages.repos import LogSmsRepo
from src.booking import repos as booking_repos
from src.notifications import repos as notification_repos
from src.notifications.services import (
    BookingNotificationService,
    CleanLogsNotificationService,
    SendSMSBookingNotifyService,
    BookingFixationNotificationService,
    SendEmailBookingFixationNotifyService,
    GetEmailTemplateService,
)


@celery.app.task
def periodic_notification_logs_clean() -> None:
    """
    Чистка логов отправленных писем и смс старше 14 дней.
    """
    days: int = logs_config.get("logs_notification_lifetime")
    resources: dict[str, Any] = dict(
        log_email_repo=LogEmailRepo,
        log_sms_repo=LogSmsRepo,
        orm_class=Tortoise,
        orm_config=tortoise_config,
    )
    notiification_clean_logs_service: CleanLogsNotificationService = CleanLogsNotificationService(**resources)
    loop: Any = get_event_loop()
    loop.run_until_complete(celery.sentry_catch(celery.init_orm(notiification_clean_logs_service))(days))


@celery.app.task
def booking_notification_sms_task(booking_id: int) -> None:
    """
    Запускаем отложенные таски по отправке смс за N часов до конца бронирования.
    """
    resources: dict[str, Any] = dict(
        booking_repo=booking_repos.BookingRepo,
        booking_notification_repo=notification_repos.BookingNotificationRepo,
        send_booking_notify_sms_task=send_booking_notify_sms_task,
        orm_class=Tortoise,
        orm_config=tortoise_config,
    )
    booking_sms_notification_service: BookingNotificationService = BookingNotificationService(**resources)
    loop: Any = get_event_loop()
    loop.run_until_complete(
        celery.sentry_catch(celery.init_orm(booking_sms_notification_service))(booking_id=booking_id)
    )


@celery.app.task
def send_booking_notify_sms_task(data: dict[str, Any]) -> None:
    """
    Уведомление о бронировании по смс за N часов до конца бронирования.
    """
    resources: dict[str, Any] = dict(
        booking_repo=booking_repos.BookingRepo,
        booking_notification_repo=notification_repos.BookingNotificationRepo,
        sms_class=messages.SmsService,
        orm_class=Tortoise,
        orm_config=tortoise_config,
        send_booking_notify_sms_task=send_booking_notify_sms_task,
    )
    send_booking_notify_service: SendSMSBookingNotifyService = SendSMSBookingNotifyService(**resources)
    loop: Any = get_event_loop()
    loop.run_until_complete(
        celery.sentry_catch(celery.init_orm(send_booking_notify_service))(data=data)
    )


@celery.app.task
def booking_fixation_notification_email_task(booking_id: int) -> None:
    """
    Запускаем отложенные таски по отправке писем за N часов до окончания фиксации и при окончании фиксации.
    """
    resources: dict[str, Any] = dict(
        booking_repo=booking_repos.BookingRepo,
        booking_fixation_notification_repo=notification_repos.BookingFixationNotificationRepo,
        send_booking_fixation_notify_email_task=send_booking_fixation_notify_email_task,
        orm_class=Tortoise,
        orm_config=tortoise_config,
    )
    booking_email_fixation_notification_service: BookingFixationNotificationService = \
        BookingFixationNotificationService(**resources)
    loop: Any = get_event_loop()
    loop.run_until_complete(
        celery.sentry_catch(celery.init_orm(booking_email_fixation_notification_service))(booking_id=booking_id)
    )


@celery.app.task
def send_booking_fixation_notify_email_task(data: dict[str, Any]) -> None:
    """
    Уведомление об окончании фиксации по почте за N часов до конца фиксации и в момент окончания фиксации.
    """
    get_email_template_service: GetEmailTemplateService = \
        GetEmailTemplateService(
            email_template_repo=notification_repos.EmailTemplateRepo,
        )
    resources: dict[str, Any] = dict(
        booking_repo=booking_repos.BookingRepo,
        booking_settings_repo=BookingSettingsRepo,
        booking_fixation_notification_repo=notification_repos.BookingFixationNotificationRepo,
        email_class=email.EmailService,
        orm_class=Tortoise,
        orm_config=tortoise_config,
        get_email_template_service=get_email_template_service,
    )
    send_booking_fixation_notify_service: SendEmailBookingFixationNotifyService = \
        SendEmailBookingFixationNotifyService(**resources)
    loop: Any = get_event_loop()
    loop.run_until_complete(
        celery.sentry_catch(celery.init_orm(send_booking_fixation_notify_service))(data=data)
    )
