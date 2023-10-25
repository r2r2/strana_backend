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
from kombu import Queue, Exchange
from sentry_sdk import capture_exception
from sentry_sdk import init as sentry_init
from sentry_sdk.integrations.celery import CeleryIntegration


class CeleryTaskQueue:
    """
    Celery setup
    """
    _q_tasks: str = "tasks"  # Название очереди
    _q_periodic_tasks: str = "periodic_tasks"  # Название очереди периодических задач
    _worker_tasks: list[str] = [  # Имена воркеров (hostname@domain)
        "tasks@strana.com",
    ]
    # _worker_periodic_tasks: list[str] = [  # Имена воркеров периодических задач (hostname@domain)
    #     "periodic_tasks@strana.com",
    # ]

    def __init__(self, config: dict[str, Any]) -> None:
        self._config: dict[str, Any] = config
        self._queue: type[Queue] = Queue
        self._priority: Priority = Priority(steps=10)

        self._app: Celery = Celery(broker=self._config["broker_url"])

    @property
    def app(self) -> Celery:
        return self._app

    def setup(self) -> None:
        self._import_tasks()
        self._setup_app_conf()
        self._add_workers()
        
    @property
    def _tasks(self) -> dict[str, tuple[str, int]]:
        """
        Нужно указать:
            ключ словаря - путь до модуля с тасками
            значение словаря - кортеж из названия очереди и приоритета
        """
        return {
            "src.booking.tasks": (self._q_tasks, self._priority.highest),
            "src.users.tasks": (self._q_tasks, self._priority.high),
            "src.properties.tasks": (self._q_tasks, self._priority.middle),
            "src.agencies.tasks": (self._q_tasks, self._priority.high),
            "src.agents.tasks": (self._q_tasks, self._priority.high),
            "src.represes.tasks": (self._q_tasks, self._priority.high),
            "common.amocrm.tasks": (self._q_tasks, self._priority.high),
            "src.cities.tasks": (self._q_tasks, self._priority.low),
            "src.amocrm.tasks": (self._q_tasks, self._priority.low),
            "src.task_management.tasks": (self._q_tasks, self._priority.high),
            "src.notifications.tasks": (self._q_tasks, self._priority.low),
            "src.events.tasks": (self._q_tasks, self._priority.low),
        }

    def _import_tasks(self) -> None:
        """
        Import tasks
        """
        [import_module(module) for module in self._tasks.keys()]

    def _setup_app_conf(self) -> None:
        """
        Celery app conf setup
        """
        self._app.conf.timezone = self._config["timezone"]
        self._app.conf.result_backend = self._config["result_backend"]
        self._app.conf.accept_content = self._config["accept_content"]
        self._app.conf.task_serializer = self._config["task_serializer"]
        self._app.conf.result_serializer = self._config["result_serializer"]
        self._app.conf.task_queues = self._queues
        self._app.conf.task_track_started = True
        self._app.conf.broker_transport_options = self._broker_transport_options
        self._app.conf.task_routes = self._task_routes
        self._app.conf.beat_schedule = self._beat_schedule
        self._app.conf.beat_cron_starting_deadline = 60 * 5  # seconds
        self._app.conf.worker_prefetch_multiplier = 1

    def _add_workers(self) -> None:
        """
        Add workers
        """
        self._app.control.add_consumer(
            self._q_tasks,
            reply=True,
            destination=self._worker_tasks,
            # exchange=self._q_tasks,
            # routing_key=self._q_tasks,
        )
        # self._app.control.add_consumer(
        #     self._q_periodic_tasks,
        #     reply=True,
        #     destination=self._worker_periodic_tasks,
        #     exchange=self._q_periodic_tasks,
        #     routing_key=self._q_periodic_tasks,
        # )

    @property
    def _queues(self) -> tuple[Queue, ...]:
        """
        Celery queues setup
        """
        return (
            self._queue(
                name=self._q_tasks,
                # exchange=Exchange(self._q_tasks),
                # routing_key=self._q_tasks,
            ),
            # self._queue(
            #     name=self._q_periodic_tasks,
            #     exchange=Exchange(self._q_periodic_tasks),
            #     routing_key=self._q_periodic_tasks,
            # ),
        )

    @property
    def _broker_transport_options(self) -> dict[str, Any]:
        return {
            'priority_steps': self._priority.steps,
            'sep': ':',
            'queue_order_strategy': 'priority',
        }

    @property
    def _task_routes(self) -> dict[str, dict[str, Any]]:
        return {
            f"{key}.*": {
                "queue": value[0],
                "task_default_priority": value[1],
                # "exchange": value[0],
                # "routing_key": value[0],
            } for key, value in self._tasks.items()
        }

    @property
    def _beat_schedule(self) -> dict[str, dict[str, Any]]:
        """
        Celery beat schedule setup
        """
        return {
            "check_organization_task_periodic": {
                "schedule": crontab(hour="*/1", minute='0'),
                "task": "src.agencies.tasks.check_organization_task_periodic",
                "options": {
                    "priority": self._priority.low,
                    # "queue": self._q_periodic_tasks,
                    # "exchange": self._q_periodic_tasks,
                    # "routing_key": self._q_periodic_tasks,
                }
            },
            "check_client_task_periodic": {
                "schedule": crontab(hour="0", minute='0'),
                "task": "src.users.tasks.check_client_task_periodic",
                "options": {
                    "priority": self._priority.low,
                    # "queue": self._q_periodic_tasks,
                    # "exchange": self._q_periodic_tasks,
                    # "routing_key": self._q_periodic_tasks,
                }
            },
            # "deactivate_expired_bookings_task_periodic": {
            #     "schedule": crontab(minute="*/10"),
            #     "task": "src.booking.tasks.deactivate_expired_bookings_task_periodic",
            #     "options": {
            #         "priority": self._priority.middle,
            #         "queue": self._q_periodic_tasks,
            #         "exchange": self._q_periodic_tasks,
            #         "routing_key": self._q_periodic_tasks,
            #     }
            # },
            "update_properties_task_periodic": {
                "schedule": crontab(minute="0", hour="0", day_of_month='*/1'),
                "task": "src.properties.tasks.import_properties_task_periodic",
                "options": {
                    "priority": self._priority.middle,
                    # "queue": self._q_periodic_tasks,
                    # "exchange": self._q_periodic_tasks,
                    # "routing_key": self._q_periodic_tasks,
                }
            },
            "update_bookings_task_periodic": {
                "schedule": crontab(hour='*/1', minute='0'),
                "task": "src.booking.tasks.update_bookings_task",
                "options": {
                    "priority": self._priority.middle,
                    # "queue": self._q_periodic_tasks,
                    # "exchange": self._q_periodic_tasks,
                    # "routing_key": self._q_periodic_tasks,
                }
            },
            "update_pipeline_statuses": {
                "schedule": crontab(hour='*/1', minute='0'),
                "task": "common.amocrm.tasks.update_amocrm_statuses_periodic",
                "options": {
                    "priority": self._priority.middle,
                    # "queue": self._q_periodic_tasks,
                    # "exchange": self._q_periodic_tasks,
                    # "routing_key": self._q_periodic_tasks,
                }
            },
            "import_cities_periodic": {
                "schedule": crontab(hour='*/1', minute='0'),
                "task": "src.cities.tasks.periodic_cities_update_task",
                "options": {
                    "priority": self._priority.middle,
                    # "queue": self._q_periodic_tasks,
                    # "exchange": self._q_periodic_tasks,
                    # "routing_key": self._q_periodic_tasks,
                }
            },
            "import_amocrm_periodic": {
                "schedule": crontab(hour='*/1', minute='0'),
                "task": "src.amocrm.tasks.import_amocrm_periodic",
                "options": {
                    "priority": self._priority.middle,
                    # "queue": self._q_periodic_tasks,
                }
            },
            "check_user_interests": {
                "schedule": crontab(minute="0", hour="5", day_of_month='*/1'),
                "task": "src.users.tasks.check_user_interests",
                "options": {
                    "priority": self._priority.middle,
                    # "queue": self._q_periodic_tasks,
                    # "exchange": self._q_periodic_tasks,
                    # "routing_key": self._q_periodic_tasks,
                }
            },
            "periodic_users_clean": {
                "schedule": crontab(minute="0", hour="0", day_of_week="0"),
                "task": "src.users.tasks.periodic_users_clean",
                "options": {
                    "priority": self._priority.low,
                    # "queue": self._q_periodic_tasks,
                    # "exchange": self._q_periodic_tasks,
                    # "routing_key": self._q_periodic_tasks,
                }
            },
            "periodic_logs_clean": {
                "schedule": crontab(minute="0", hour="0", day_of_month='*/1'),
                "task": "src.users.tasks.periodic_logs_clean",
                "options": {
                    "priority": self._priority.low,
                    # "queue": self._q_periodic_tasks,
                    # "exchange": self._q_periodic_tasks,
                    # "routing_key": self._q_periodic_tasks,
                }
            },
            "periodic_notification_logs_clean": {
                "schedule": crontab(minute="0", hour="0", day_of_month='*/1'),
                "task": "src.notifications.tasks.periodic_notification_logs_clean",
                "options": {
                    "priority": self._priority.low,
                    # "queue": self._q_periodic_tasks,
                    # "exchange": self._q_periodic_tasks,
                    # "routing_key": self._q_periodic_tasks,
                }
            },
            "periodic_update_missed_amocrm_id_task": {
                # "schedule": crontab(minute=0, hour='21'),
                "schedule": crontab(hour='*/1', minute='0'),
                "task": "src.agencies.tasks.periodic_update_missed_amocrm_id_task",
                "options": {
                    "priority": self._priority.low,
                    # "queue": self._q_periodic_tasks,
                    # "exchange": self._q_periodic_tasks,
                    # "routing_key": self._q_periodic_tasks,
                }
            },
        }


task_queue: CeleryTaskQueue = CeleryTaskQueue(config=celery_config)
app: Celery = task_queue.app
# Настройка после получения инстанса Celery
task_queue.setup()


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
