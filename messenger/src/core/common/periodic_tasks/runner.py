import asyncio
from dataclasses import dataclass
from datetime import timedelta
from functools import partial
from typing import Any, Callable, Coroutine, Self

from src.core.logger import LoggerName, get_logger
from src.exceptions import InternalError
from src.jobs.base_settings import JobSettings


@dataclass
class PeriodicTask:
    name: str
    is_enabled: bool
    call_interval: timedelta
    coro: Callable[[], Coroutine[Any, Any, None]]
    debug: bool


class PeriodicTasksRunner:
    def __init__(self) -> None:
        self.logger = get_logger(LoggerName.PERIODIC_TASKS)
        self._tasks: list[PeriodicTask] = []
        self._scheduled_tasks: dict[str, asyncio.TimerHandle] = {}
        self._running_tasks: list[asyncio.Task[None]] = []
        self._is_running = False

    def start(self, start_immediately: bool) -> None:
        if self._is_running:
            raise InternalError("Runner is already running")

        self._is_running = True

        for task in self._tasks:
            wait_time = 0 if start_immediately else task.call_interval.total_seconds()
            self._schedule_task(wait_time, task)

    async def stop(self, wait_for_completion: bool) -> None:
        self._is_running = False
        for scheduled in self._scheduled_tasks.values():
            scheduled.cancel()

        wait_for = []
        for running in self._running_tasks:
            running.cancel()
            if wait_for_completion:
                wait_for.append(running)

        if wait_for:
            await asyncio.gather(*wait_for, return_exceptions=True)

    def _schedule_task(self, call_after: int | float, task: PeriodicTask) -> None:
        if task.name in self._scheduled_tasks:
            raise InternalError(f"Task {task.name} is already scheduled")

        loop = asyncio.get_running_loop()
        call_handle = loop.call_later(call_after, self._start_task, task)
        self._scheduled_tasks[task.name] = call_handle
        if task.debug:
            self.logger.debug(f"Task {task.name} scheduled to run after {call_after} seconds")

    def _start_task(self, task: PeriodicTask) -> None:
        self._scheduled_tasks.pop(task.name)
        if task.debug:
            self.logger.debug(f"Starting task {task.name}")

        if not task.is_enabled:
            if task.debug:
                self.logger.debug(f"Task {task.name} is disabled, skipping")
            return

        asyncio_task = asyncio.create_task(task.coro())
        asyncio_task.add_done_callback(partial(self._handle_task_finish, task))
        self._running_tasks.append(asyncio_task)

    def add_task(
        self,
        task_name: str,
        call_interval: timedelta,
        coro: Callable[[], Coroutine[Any, Any, None]],
        settings: JobSettings,
    ) -> Self:
        task = PeriodicTask(
            name=task_name,
            is_enabled=settings.is_enabled,
            call_interval=call_interval,
            coro=coro,
            debug=settings.debug,
        )
        self._tasks.append(task)
        if self._is_running:
            self._schedule_task(task.call_interval.total_seconds(), task)

        return self

    def _handle_task_finish(self, task: PeriodicTask, result: asyncio.Task[None]) -> None:
        if task.debug:
            self.logger.debug(f"Task {task.name} finished")

        try:
            result.result()

        except asyncio.CancelledError:
            if task.debug:
                self.logger.debug(f"Task {task.name} was cancelled")

        except Exception as exc:
            self.logger.warning(
                f"Unhandled exception in task {task.name}",
                exc_info=exc,
            )

        finally:
            self._running_tasks.remove(result)
            if self._is_running:
                self._schedule_task(task.call_interval.total_seconds(), task)
