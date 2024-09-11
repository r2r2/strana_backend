from typing import Awaitable, Callable, Concatenate

from src.core.common.caching import default_method_key_builder
from src.core.logger import get_logger
from src.core.types import P, RedisConn
from src.providers.time import timestamp_now


class Throttler:
    def __init__(self, conn: RedisConn, namespace: str) -> None:
        self.conn = conn
        self.namespace = namespace
        self.logger = get_logger("throttler")

    def throttled_func(
        self,
        func: Callable[P, Awaitable[None]],
        throttle_time: int,
    ) -> Callable[Concatenate[str | None, P], Awaitable[None]]:
        async def _inner(key_name: str | None = None, /, *args: P.args, **kwargs: P.kwargs) -> None:
            if not key_name:
                key_name = default_method_key_builder(func, *args, **kwargs)

            namespaced_key = self.namespace + key_name

            if await self.conn.get(namespaced_key):
                return

            await self.conn.set(namespaced_key, timestamp_now(), ex=throttle_time)
            await func(*args, **kwargs)

        return _inner
