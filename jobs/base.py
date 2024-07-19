import abc
import asyncio
import logging
import time
import traceback
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from logging import Logger, LoggerAdapter
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from aio_pika import connect_robust
from aio_pika.abc import AbstractChannel, AbstractQueue
from boilerplates.logging import get_logger
from celery import Task
from redis.asyncio import Redis
from sl_slack_logger import setup_slack_logger_ctx
from sqlalchemy.orm import sessionmaker
from structlog.typing import FilteringBoundLogger

from jobs.constants import QUEUE_INTERNAL_NAME
from jobs.internal.app_settings import BaseJobSettings, Settings
from sdk.db.utils import create_engine
from sdk.internal.app_settings import RegisteredQueuesSettings

if TYPE_CHECKING:
    _LoggerAdapter = LoggerAdapter[Logger]
else:
    _LoggerAdapter = LoggerAdapter

JobSettings = TypeVar("JobSettings", bound=BaseJobSettings)


class BaseJob(Task, Generic[JobSettings], metaclass=abc.ABCMeta):
    _settings: Settings
    _logger: FilteringBoundLogger
    _session_maker: sessionmaker
    _sl_implan_session_maker: sessionmaker
    _lp_dump_session_maker: sessionmaker
    _channel: AbstractChannel
    _queue: AbstractQueue
    _redis: "Redis[Any]"
    description: str = ""
    name: str

    @property
    def job_settings(self) -> JobSettings:
        return getattr(self._settings.registered_jobs, self.name)  # type: ignore

    @property
    def registered_queues(self) -> RegisteredQueuesSettings:
        return self._settings.registered_queues

    @abc.abstractmethod
    async def _run_async(self) -> None:
        ...

    def run(self) -> None:
        asyncio.run(self._run_in_local_lifespan())

    def inject_settings(self, settings: Settings) -> None:
        self._settings = settings

    async def _run_in_local_lifespan(self) -> None:
        async with self.lifespan():
            await self._run_async()

    @asynccontextmanager
    async def lifespan(self) -> AsyncIterator[None]:
        self._logger = get_logger(self.name)
        start = time.time()

        self._redis = Redis(
            host=self._settings.redis.host,
            port=self._settings.redis.port,
            db=self._settings.redis.database,
            password=self._settings.redis.password.get_secret_value(),
            decode_responses=True,
        )

        engine, self._session_maker = create_engine(self._settings.postgres)
        sl_implan_engine, self._sl_implan_session_maker = create_engine(
            self._settings.sl_implan_postgres,
            isolation_level="AUTOCOMMIT",
        )
        lp_dump_engine, self._lp_dump_session_maker = create_engine(
            self._settings.lp_dump_postgres,
            isolation_level="AUTOCOMMIT",
        )
        connection = await connect_robust(
            host=self._settings.rabbit.host,
            virtualhost=self._settings.rabbit.vhost,
            login=self._settings.rabbit.username,
            password=self._settings.rabbit.password.get_secret_value(),
        )

        self._channel = await connection.channel()
        self._queue = await self._channel.declare_queue(name=QUEUE_INTERNAL_NAME, durable=True)

        async with setup_slack_logger_ctx(
            slack_config=self._settings.slack,
            loggers=[logging.getLogger()],
            log_level=logging.WARNING,
        ):

            try:
                self._logger.info("Start")
                if self.description:
                    self._logger.info(f"Описание: {self.description}")
                yield
            except Exception as e:  # noqa: PIE786
                self._logger.warning(traceback.format_exc())
                raise e
            finally:
                time_taken = round(time.time() - start, 2)
                self._logger.info(f"Finish, время выполнения: {time_taken} сек.")
                await asyncio.gather(
                    self._redis.close(),
                    engine.dispose(),
                    sl_implan_engine.dispose(),
                    lp_dump_engine.dispose(),
                    connection.close(),
                )
