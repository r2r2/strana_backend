from asyncio import get_event_loop
from typing import Any

from config import celery, tortoise_config, logs_config
from tortoise import Tortoise
from common.email.repos import LogEmailRepo
from common.messages.repos import LogSmsRepo
from src.notifications.services import CleanLogsNotificationService


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
