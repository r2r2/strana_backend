from datetime import timedelta
from typing import Any

from boilerplates.logging import LoggingConfig, setup_logging
from celery import Celery
from celery.signals import celeryd_init
from celery.signals import setup_logging as setup_celery_logging_signal
from celery.signals import worker_ready
from celery.worker.consumer import Consumer
from sentry_sdk.integrations.celery import CeleryIntegration

from jobs.base import BaseJob
from jobs.constants import SENTRY_APP_NAME
from jobs.internal.app_settings import Settings
from jobs.settings import get_config
from sdk.sentry import init_sentry


def create_app() -> Celery:
    settings = get_config()
    return Celery(
        settings.job.app_name,
        broker_url=settings.rabbit.dsn,
        include=["jobs.tasks"],
    )


def setup_jobs(celery_app: Celery, settings: Settings) -> None:
    for job in (task for task in celery_app.tasks.values() if isinstance(task, BaseJob)):
        job.inject_settings(settings)
        if job.job_settings is None:
            continue
        celery_app.conf.beat_schedule |= {
            job.__class__.__name__: {
                "task": job.name,
                "schedule": job.job_settings.schedule,
                "options": {"expires": timedelta(days=1).total_seconds()},
            },
        }


@celeryd_init.connect
def setup_sentry(*args: list[Any], **kwargs: dict[str, Any]) -> None:
    settings = get_config()
    init_sentry(settings.sentry, tag_name=SENTRY_APP_NAME, integrations=[CeleryIntegration(monitor_beat_tasks=True)])


@setup_celery_logging_signal.connect
def setup_logger(*args: list[Any], **kwargs: dict[str, Any]) -> None:
    settings = get_config()
    setup_logging(
        config=LoggingConfig(
            use_colors=settings.logging.use_colors,
            log_format=settings.logging.log_format,
            log_level=settings.logging.level,
            is_sentry_enabled=settings.sentry.is_enabled,
            log_levels={logger_name: "WARNING" for logger_name in settings.logging.spammy_loggers},
        ),
    )


@worker_ready.connect
def run_startup_tasks(sender: Consumer, **kwargs: dict[str, Any]) -> None:
    startup_tasks = []
    for job in sender.app.tasks.values():
        if not isinstance(job, BaseJob):
            continue
        if job_settings := getattr(job, "job_settings", None):
            if job_settings.run_at_startup:
                startup_tasks.append(job)
    if startup_tasks:
        with sender.app.connection() as conn:
            for startup_task in startup_tasks:
                sender.app.send_task(startup_task.name, connection=conn)
