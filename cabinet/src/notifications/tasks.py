from asyncio import get_event_loop
from typing import Any

from common import email, messages
from common.settings.repos import BookingSettingsRepo
from common.celery.utils import redis_lock
from config import celery, tortoise_config, logs_config, site_config
from tortoise import Tortoise
from common.email.repos import LogEmailRepo
from common.messages.repos import LogSmsRepo
from src.booking import repos as booking_repos
from src.events_list import repos as events_list_repos
from src.notifications import repos as notification_repos
from src.notifications.services import (
    BookingNotificationService,
    CleanLogsNotificationService,
    SendSMSBookingNotifyService,
    BookingFixationNotificationService,
    SendEmailBookingFixationNotifyService,
    GetEmailTemplateService,
    CheckQRCodeSMSSend,
    SendQRCodeSMS,
)
from src.task_management.repos import TaskInstanceRepo
from src.users import repos as users_repos


@celery.app.task
def periodic_notification_logs_clean() -> None:
    """
    Чистка логов отправленных писем и смс старше 14 дней.
    """
    lock_id = "periodic_cache_periodic_notification_logs_clean"
    can_launch = redis_lock(lock_id)
    if not can_launch:
        return

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
def booking_notification_sms_task(booking_id: int) -> bool:
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
    return loop.run_until_complete(
        celery.sentry_catch(celery.init_orm(booking_sms_notification_service))(booking_id=booking_id)
    )


@celery.app.task
def send_booking_notify_sms_task(data: dict[str, Any]) -> bool:
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
    return loop.run_until_complete(
        celery.sentry_catch(celery.init_orm(send_booking_notify_service))(data=data)
    )


@celery.app.task
def periodic_booking_fixation_notification_email_task() -> None:
    """
    Запуск отложенных задач по отправке писем за N часов до окончания фиксации и при окончании фиксации
    (через eta задачи).
    """
    resources: dict[str, Any] = dict(
        task_instance_repo=TaskInstanceRepo,
        booking_fixation_notification_repo=notification_repos.BookingFixationNotificationRepo,
        booking_settings_repo=BookingSettingsRepo,
        send_booking_fixation_notify_email_task=send_booking_fixation_notify_email_task,
        orm_class=Tortoise,
        orm_config=tortoise_config,
    )
    booking_email_fixation_notification_service: BookingFixationNotificationService = \
        BookingFixationNotificationService(**resources)
    loop: Any = get_event_loop()
    loop.run_until_complete(
        celery.sentry_catch(celery.init_orm(booking_email_fixation_notification_service))()
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


@celery.app.task
def periodic_send_qrcode_sms_task() -> None:
    """
    Проверка условий для отправки смс с QR кодом участнику мероприятия.
    """
    print(f'start periodic_send_qrcode_sms_task')

    resources: dict[str, Any] = dict(
        qrcode_sms_notify_repo=notification_repos.QRcodeSMSNotifyRepo,
        send_qrcode_sms_task=send_qrcode_sms_task,
        orm_class=Tortoise,
        orm_config=tortoise_config,
    )
    check_qrcode_sms_send: CheckQRCodeSMSSend = CheckQRCodeSMSSend(**resources)
    loop: Any = get_event_loop()
    loop.run_until_complete(celery.sentry_catch(celery.init_orm(check_qrcode_sms_send))())
    print("finish periodic_send_qrcode_sms_task")


@celery.app.task
def send_qrcode_sms_task(data: dict[str, int]) -> None:
    """
    Отправка смс с QR кодом.
    """
    print(f'start send_qrcode_sms_task with {data=}')
    resources: dict[str, Any] = dict(
        event_participant_repo=events_list_repos.EventParticipantListRepo,
        qrcode_sms_notify_repo=notification_repos.QRcodeSMSNotifyRepo,
        event_list_repo=events_list_repos.EventListRepo,
        sms_class=messages.SmsService,
        site_config=site_config,
        orm_class=Tortoise,
        orm_config=tortoise_config,
    )
    send_qrcode_sms: SendQRCodeSMS = SendQRCodeSMS(**resources)
    loop: Any = get_event_loop()
    loop.run_until_complete(celery.sentry_catch(celery.init_orm(send_qrcode_sms))(data=data))
    print("finish send_qrcode_sms_task")
