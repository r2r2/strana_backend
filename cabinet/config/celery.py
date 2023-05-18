# pylint: disable=broad-except

"""
For lightweight tasks use asyncio.Future and asyncio.Task
Documentation: https://docs.python.org/3/library/asyncio-task.html
"""
import traceback
from asyncio import new_event_loop, set_event_loop
from importlib import import_module
from json import dumps
from typing import Any, Callable

from celery import Celery
from celery.schedules import crontab
from common.celery import Priority
from config import application_config, celery_config, sentry_config
from kombu import Queue
from sentry_sdk import capture_exception
from sentry_sdk import init as sentry_init
from sentry_sdk.integrations.celery import CeleryIntegration

app = Celery(broker=celery_config["broker_url"])
app.conf.timezone = celery_config["timezone"]
app.conf.result_backend = celery_config["result_backend"]
app.conf.accept_content = celery_config["accept_content"]
app.conf.task_serializer = celery_config["task_serializer"]
app.conf.result_serializer = celery_config["result_serializer"]
import_module("src.booking.tasks")
import_module("src.users.tasks")
import_module("src.properties.tasks")
import_module("src.agencies.tasks")
import_module("src.agents.tasks")
import_module("src.represes.tasks")
import_module("common.amocrm.tasks")
import_module("src.cities.tasks")
import_module("src.amocrm.tasks")
import_module("src.task_management.tasks")
app.conf.task_queues = (Queue("tasks"),)
app.control.add_consumer("tasks", reply=True, destination=["tasks@strana.com"])
priority = Priority(steps=10)
app.conf.broker_transport_options = {
    'priority_steps': priority.steps,
    'sep': ':',
    'queue_order_strategy': 'priority',
}
app.conf.task_routes = {
    "src.booking.tasks.*": {"queue": "tasks", "task_default_priority": priority.highest},
    "src.users.tasks.*": {"queue": "tasks", "task_default_priority": priority.high},
    "src.properties.tasks.*": {"queue": "tasks", "task_default_priority": priority.middle},
    "src.agencies.tasks.*": {"queue": "tasks", "task_default_priority": priority.high},
    "src.agents.tasks.*": {"queue": "tasks", "task_default_priority": priority.high},
    "src.represes.tasks.*": {"queue": "tasks", "task_default_priority": priority.high},
    "common.amocrm.tasks.*": {"queue": "tasks", "task_default_priority": priority.high},
    "src.cities.tasks.*": {"queue": "tasks", "task_default_priority": priority.low},
    "src.amocrm.tasks.*": {"queue": "tasks", "task_default_priority": priority.low},
    "src.task_management.tasks.*": {"queue": "tasks", "task_default_priority": priority.high},
}

user_interest_task_time = celery_config["user_interest_task_time"]

app.conf.beat_schedule = {
    "check_organization_task_periodic": {
        "schedule": crontab(hour="*/1", minute='0'),
        "task": "src.agencies.tasks.check_organization_task_periodic",
        "options": {
            "priority": priority.low,
        }
    },
    "check_client_task_periodic": {
        "schedule": crontab(hour="*/1", minute='0'),
        "task": "src.users.tasks.check_client_task_periodic",
        "options": {
            "priority": priority.low,
        }
    },
    # "deactivate_expired_bookings_task_periodic": {
    #     "schedule": crontab(minute="*/10"),
    #     "task": "src.booking.tasks.deactivate_expired_bookings_task_periodic",
    #     "options": {
    #         "priority": priority.middle,
    #     }
    # },
    "update_properties_task_periodic": {
        "schedule": crontab(minute=0, hour=0, day_of_month='*/1'),
        "task": "src.properties.tasks.import_properties_task_periodic",
        "options": {
            "priority": priority.middle,
        }
    },
    "update_bookings_task_periodic": {
        "schedule": crontab(minute="*/10"),
        "task": "src.booking.tasks.update_bookings_task",
        "options": {
            "priority": priority.middle,
        }
    },
    "update_pipeline_statuses": {
        "schedule": crontab(hour='*/1', minute='0'),
        "task": "common.amocrm.tasks.update_amocrm_statuses_periodic",
        "options": {
            "priority": priority.middle,
        }
    },
    "import_cities_periodic": {
        "schedule": crontab(hour='*/1', minute='0'),
        "task": "src.cities.tasks.import_cities_periodic",
        "options": {
            "priority": priority.middle,
        }
    },
    "import_amocrm_periodic": {
        "schedule": crontab(hour='*/1', minute='0'),
        "task": "src.amocrm.tasks.import_amocrm_periodic",
        "options": {
            "priority": priority.middle,
        }
    },
    "check_user_interests": {
        "schedule": crontab(
            hour=user_interest_task_time, minute=0
        ) if user_interest_task_time[0] != '*' else crontab(
            minute=user_interest_task_time
        ),
        "task": "src.users.tasks.check_user_interests",
        "options": {
            "priority": priority.middle,
        }
    },
    "periodic_users_clean": {
        "schedule": crontab(minute=0, hour=0, day_of_week=0),
        "task": "src.users.tasks.periodic_users_clean",
        "options": {
            "priority": priority.low,
        }
    },
    "periodic_logs_clean": {
        "schedule": crontab(minute=0, hour=0, day_of_month='*/1'),
        "task": "src.users.tasks.periodic_logs_clean",
        "options": {
            "priority": priority.low,
        }
    },
}

app.conf.update(task_track_started=True)


class TaskError(Exception):
    """
    Task error
    """


def init_orm(service: Callable[..., Any]) -> Callable[..., Any]:
    """
    Orm initialization on task
    """

    async def decorated(*args: list[Any], **kwargs: dict[str, Any]) -> Any:
        if hasattr(service, "orm_class") and hasattr(service, "orm_config"):
            await service.orm_class.init(config=service.orm_config)
        result: Any = await service(*args, **kwargs)
        if hasattr(service, "orm_class") and hasattr(service, "orm_config"):
            await service.orm_class.close_connections()
        return result

    return decorated


def sentry_catch(service: Callable[..., Any]) -> Callable[..., Any]:
    """
    Avoid loop breaking and capture any error to sentry
    """

    def _handle_error(error: Exception, args: tuple[Any], kwargs: dict[str, Any]):
        traceback.print_exc()
        exc: dict[str, Any] = dict(original_error=f"{error.__class__.__name__} {str(error)}")
        try:
            exc["args"]: str = dumps(args)
        except TypeError:
            pass
        try:
            exc["kwargs"]: str = dumps(kwargs)
        except TypeError:
            pass
        task_error: TaskError = TaskError(exc)
        print(str(task_error))
        capture_exception(task_error)

    async def decorated(*args, **kwargs: dict[str, Any]) -> Any:
        try:
            result: Any = await service(*args, **kwargs)
            return result
        except RuntimeError:
            try:
                set_event_loop(new_event_loop())
                result: Any = await service(*args, **kwargs)
                return result
            except Exception as error:
                _handle_error(error=error, args=args, kwargs=kwargs)
        except Exception as error:
            _handle_error(error=error, args=args, kwargs=kwargs)

    return decorated


if __name__ == "__main__":
    app.start()
    if not application_config["debug"]:
        sentry_init(dsn=sentry_config["dsn"], integrations=[CeleryIntegration()])
