import asyncio
from inspect import iscoroutinefunction
from typing import Any, Callable, Self

from aiojobs import Scheduler
from redis.asyncio.client import PubSub
from redis.exceptions import ConnectionError as RedisConnectionError

from src.core.common.redis.helpers import is_redis_conn_healthy, load_script_content
from src.core.logger import LoggerName, get_logger
from src.core.types import RedisConn


class RedisPublisher:
    def __init__(
        self,
        conn: RedisConn,
        jobs_warning_threshold: int,
        max_concurrent_jobs: int,
        max_pending_jobs: int,
    ) -> None:
        self.redis_conn = conn
        self.jobs_scheduler = Scheduler(
            close_timeout=5.0,
            limit=max_concurrent_jobs,
            pending_limit=max_pending_jobs,
        )
        self.logger = get_logger(LoggerName.PUBSUB)
        self.decr_many = self.redis_conn.register_script(load_script_content("decrement_many_if_exists"))
        self.incr_many = self.redis_conn.register_script(load_script_content("increment_many_if_exists"))

        self._jobs_warning_threshold = jobs_warning_threshold
        self._max_concurrent_jobs = max_concurrent_jobs
        self._max_pending_jobs = max_pending_jobs

    async def health_check(self) -> bool:
        return await is_redis_conn_healthy(self.redis_conn)

    async def send_to(self, channel_name: str, data: bytes, on_error: Callable[..., Any] | None = None) -> None:
        coro = self.publish(channel_name, data, on_error)
        await self.jobs_scheduler.spawn(coro)
        self._check_active_jobs()

    async def publish(
        self,
        channel_name: str,
        data: bytes,
        on_error: Callable[..., Any] | None = None,
        warn_no_consumers_found: bool = True,
    ) -> None:
        result = await self.redis_conn.publish(channel_name, data)

        if not result and warn_no_consumers_found:
            # No subscribers found for the message
            self.logger.warning("Message was not consumed, the connection may be broken", channel_name=channel_name)

            if on_error:
                if iscoroutinefunction(on_error):
                    await on_error()
                else:
                    on_error()

    def _check_active_jobs(self) -> None:
        if self.jobs_scheduler.active_count > self._jobs_warning_threshold:
            self.logger.warning(
                f"Too many active jobs: {self.jobs_scheduler.active_count} (limit {self._jobs_warning_threshold})",
            )


class RedisListener:
    def __init__(
        self,
        conn: RedisConn,
        callback: Callable[..., Any],
        polling_interval: float | None = 3.0,
    ) -> None:
        self.logger = get_logger(LoggerName.PUBSUB)

        self._redis_conn = conn
        self._reader: asyncio.Task[Any] | None = None
        self._callback = callback
        self._subs: set[str] = set()
        self._pubsub: PubSub = self._redis_conn.pubsub(ignore_subscribe_messages=True)
        self._polling_interval = polling_interval

    async def __aenter__(self) -> Self:
        await self.start()
        return self

    async def __aexit__(self, *args: Any, **kwargs: Any) -> None:
        await self.stop()

    @property
    def is_running(self) -> bool:
        return self._reader is not None

    async def health_check(self) -> bool:
        return self.is_running and await is_redis_conn_healthy(self._redis_conn)

    async def start(self) -> None:
        await self._pubsub.connect()  # type: ignore
        self._reader = asyncio.create_task(self._reader_task(self._pubsub))

    async def subscribe(self, channel_name: str) -> None:
        if channel_name in self._subs:
            self.logger.warning(f"Already subscribed to channel: {channel_name}")
            return

        await self._pubsub.subscribe(channel_name)
        self._subs.add(channel_name)
        self.logger.debug(f"Subscribed to channel: {channel_name}")

    async def unsubscribe(self, channel_name: str) -> None:
        if channel_name not in self._subs:
            self.logger.warning(f"Not subscribed to channel: {channel_name}")
            return

        await self._pubsub.unsubscribe(channel_name)
        self._subs.remove(channel_name)
        self.logger.debug(f"Unsubscribed from channel: {channel_name}")

    async def stop(self) -> None:
        await self._pubsub.reset()
        if self._reader:
            self._reader.cancel()
            await self._reader
            self._reader = None

        self._subs.clear()
        self.logger.debug("Listening stopped")

    async def _reader_task(self, pubsub: PubSub) -> None:
        data = None
        try:
            while True:
                if msg := await pubsub.get_message(
                    ignore_subscribe_messages=True,
                    timeout=self._polling_interval or 0,
                ):
                    await self._callback(msg["data"])

        except RedisConnectionError:
            self.logger.info("Connection is closed, stopping reader task")
            return

        except RuntimeError:
            if pubsub.connection is None:
                self.logger.info("Connection is closed, stopping reader task")
                return

        except asyncio.CancelledError:
            self.logger.info("Reader task was cancelled")
            return

        except Exception:  # pylint: disable=broad-except
            self.logger.error("Error when processing message", last_data=data, exc_info=True)

        finally:
            self.logger.debug("Reader task exited")
