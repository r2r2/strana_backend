import time
from functools import lru_cache
from typing import Any

import redis.asyncio as redis
from redis.asyncio.retry import Retry
from redis.backoff import ExponentialBackoff
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import TimeoutError as RedisTimeoutError

from src.constants import LUA_SCRIPTS_FOLDER
from src.core.common.redis.settings import RedisSettings
from src.core.logger import get_logger
from src.core.types import RedisConn


class RedisWithProfiler(redis.Redis):  # type: ignore
    def __init__(self, *args: Any, slow_query_time_threshold: float, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._profiling_logger = get_logger("profiling")
        self._slow_query_time_threshold = slow_query_time_threshold

    async def execute_command(self, *args: Any, **options: Any) -> Any:
        tstart = time.perf_counter()
        result = await super().execute_command(*args, **options)
        tend = time.perf_counter()
        total = tend - tstart
        if total >= self._slow_query_time_threshold:
            self._profiling_logger.warning(
                "Slow redis query",
                total=total,
                args=args,
            )

        return result


def create_redis_conn_pool(settings: RedisSettings) -> RedisConn:
    pool = redis.ConnectionPool(
        max_connections=settings.max_connections,
        host=settings.host,
        port=settings.port,
        db=settings.db,
        retry=Retry(ExponentialBackoff(), settings.reconnect_max_retries),
        retry_on_error=[RedisTimeoutError, RedisConnectionError],
        password=settings.password.get_secret_value() if settings.password else None,
        username=settings.username,
    )

    if settings.is_profiling_enabled:
        return RedisWithProfiler(
            connection_pool=pool,
            slow_query_time_threshold=settings.slow_query_time_threshold,
        )

    return redis.Redis(connection_pool=pool)


async def is_redis_conn_healthy(conn: RedisConn) -> bool:
    return await conn.ping()


@lru_cache
def load_script_content(script_name: str) -> str:
    with open(LUA_SCRIPTS_FOLDER / f"{script_name}.lua", "r", encoding="utf8") as file:
        return file.read()
