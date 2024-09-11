from asyncio import create_task
from typing import Any, Callable

from aiocache.decorators import cached as aiocache_single_cached
from aiocache.decorators import multi_cached as aiocache_multi_cached
from aiocache.serializers import BaseSerializer

from src.core.logger import LoggerName, get_logger


class IntegerSerializer(BaseSerializer):
    def __init__(self, *args: Any, **kwargs: Any):
        self.encoding = "utf-8"

    def dumps(self, value: int) -> str:
        return str(value)

    def loads(self, value: str) -> int | None:
        try:
            return int(value)

        except Exception:
            return None


class CustomSingleCached(aiocache_single_cached):
    @property
    def debug(self) -> bool:
        return self._kwargs.get("debug", False)

    async def decorator(
        self,
        f: Callable[..., Any],
        *args: Any,
        cache_read: bool = True,
        cache_write: bool = True,
        aiocache_wait_for_write: bool = True,
        **kwargs: Any,
    ):
        key = self.get_cache_key(f, args, kwargs)

        if cache_read:
            value = await self.get_from_cache(key)
            if value is not None:
                if self.debug:
                    get_logger(LoggerName.CACHER).debug(
                        "Retrieved cached result",
                        cache_type="single",
                        key=key,
                        value=str(value),
                    )

                return value

        result = await f(*args, **kwargs)

        if self.skip_cache_func(result):
            return result

        if cache_write:
            if aiocache_wait_for_write:
                await self.set_in_cache(key, result)
            else:
                create_task(self.set_in_cache(key, result))

        if self.debug:
            get_logger(LoggerName.CACHER).debug(
                "Set new value in cache",
                cache_type="single",
                key=key,
                value=str(result),
            )

        return result


class CustomMultiCached(aiocache_multi_cached):
    """
    Patched multi_cached decorator to work with keys_from_attr and key_builder correctly and pass unchanged arguments
    to the decorated function
    """

    @property
    def debug(self) -> bool:
        return self._kwargs.get("debug", False)

    async def decorator(
        self,
        f: Callable[..., Any],
        *args: Any,
        cache_read: bool = True,
        cache_write: bool = True,
        aiocache_wait_for_write: bool = True,
        **kwargs: Any,
    ):
        missing_keys = []
        partial = {}
        keys, new_args, args_index = self.get_cache_keys(f, args, kwargs)

        keys_mapping = dict(zip(keys, kwargs.get(self.keys_from_attr, []), strict=True))
        reverse_keys_mapping = {v: k for k, v in keys_mapping.items()}

        if cache_read:
            values = await self.get_from_cache(*keys)
            for key, value in zip(keys_mapping.values(), values, strict=True):
                if value is None:
                    missing_keys.append(key)
                else:
                    partial[key] = value

            if self.debug:
                get_logger(LoggerName.CACHER).debug(
                    "Rerieved cached results",
                    cache_type="multi",
                    keys=str(keys),
                    values=str(partial),
                )

            if values and None not in values:
                return partial

        else:
            missing_keys = [reverse_keys_mapping[k] for k in keys]

        if args_index > -1:
            new_args[args_index] = missing_keys
        else:
            kwargs[self.keys_from_attr] = missing_keys

        result = await f(*new_args, **kwargs)
        to_cache = {k: v for k, v in result.items() if not self.skip_cache_func(k, v)}

        result.update(partial)

        if not to_cache:
            return result

        if cache_write:
            if self.debug:
                get_logger(LoggerName.CACHER).debug(
                    "Set new values in cache",
                    cache_type="multi",
                    keys=str(keys),
                    values=str(to_cache),
                )

            if aiocache_wait_for_write:
                await self.set_in_cache(to_cache, f, args, kwargs)
            else:
                create_task(self.set_in_cache(to_cache, f, args, kwargs))

        return result
