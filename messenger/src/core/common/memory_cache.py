import contextlib
from functools import wraps
from typing import Any, Awaitable, Callable

from cachetools import Cache

from src.core.logger import LoggerName, get_logger
from src.core.types import P, RetType

from .caching import CacherProto, CacheStatistics, default_method_key_builder


class InMemoryCacher(CacherProto):
    def __init__(self, cache: Cache[Any, Any], debug: bool = False) -> None:
        self._cache = cache
        self._debug = debug
        self._logger = get_logger(LoggerName.ROOT).bind(subtype="InMemoryCache")
        self._stats = CacheStatistics.empty()

    def get_statistics(self) -> CacheStatistics:
        self._stats.refresh()
        return self._stats

    async def invalidate_key(self, key: str) -> None:
        self._cache.pop(key, None)

    async def invalidate(
        self,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self._cache.pop(default_method_key_builder(func, *args, **kwargs), None)

    def cached_func(
        self,
        func: Callable[P, Awaitable[RetType]],
        noself: bool,
        ttl: int | None = None,
        key_builder: Callable[..., str] = default_method_key_builder,
    ) -> Callable[P, Awaitable[RetType]]:
        if ttl:
            self._logger.warning(f"Using TTL {ttl} for {func.__name__} is not supported by {self.__class__.__name__}")

        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> RetType:
            self._stats.total += 1
            kb_self = args[0] if not noself else None
            key = key_builder(kb_self, *args, **kwargs)

            with contextlib.suppress(KeyError):
                val = self._cache[key]
                self._stats.hits += 1
                if self._debug:
                    self._logger.debug(f"Get {key}: {val}")

                return val

            result = await func(*args, **kwargs)

            with contextlib.suppress(ValueError):  # Value too large, cachetools impl
                self._cache[key] = result
                if self._debug:
                    self._logger.debug(f"Set {key}: {result}")

            return result

        return wrapper

    def cached_multi_func(
        self,
        keys_kwarg: str,
        func: Callable[P, Awaitable[RetType]],
        ttl: int | None,
        noself: bool,
        key_builder: Callable[..., str] = default_method_key_builder,
    ) -> Callable[P, Awaitable[RetType]]:
        raise NotImplementedError


__all__ = ("InMemoryCacher",)
