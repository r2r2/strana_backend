from pickle import HIGHEST_PROTOCOL
from typing import Any, Awaitable, Callable, Type

from aiocache import caches
from aiocache.backends.redis import RedisCache
from aiocache.plugins import HitMissRatioPlugin, TimingPlugin
from aiocache.serializers import BaseSerializer, PickleSerializer

from src.core.common.caching import CacherProto, CacheStatistics, default_method_key_builder
from src.core.common.redis.lib import CustomMultiCached, CustomSingleCached
from src.core.common.redis.settings import RedisSettings
from src.core.types import P, RetType


class RedisCacher(CacherProto):
    def __init__(
        self,
        settings: RedisSettings,
        alias: str,
        namespace: str = "",
        default_ttl: int | None = None,
        serializer: Type[BaseSerializer] = PickleSerializer,
        serializer_kwargs: dict[str, Any] | None = None,
    ) -> None:
        self._alias = f"redis-{alias}"
        self._default_ttl = default_ttl
        self.namespace = namespace
        self.debug = settings.debug

        if not serializer_kwargs:
            serializer_kwargs = {"protocol": HIGHEST_PROTOCOL}

        caches.add(
            self._alias,
            {
                "cache": RedisCache,
                "endpoint": settings.host,
                "port": settings.port,
                "db": settings.db,
                "pool_max_size": settings.max_connections,
                "password": settings.password.get_secret_value() if settings.password else None,
                "namespace": namespace,
                "serializer": {
                    "class": serializer,
                    **serializer_kwargs,
                },
                "plugins": [
                    {"class": HitMissRatioPlugin},
                    {"class": TimingPlugin},
                ],
            },
        )
        self.cache: RedisCache = caches.get(self._alias)  # type: ignore

    def get_statistics(self) -> CacheStatistics:
        hits_stats = getattr(self.cache, "hit_miss_ratio", {})

        return CacheStatistics(
            profiling=getattr(self.cache, "profiling", {}),
            hits=hits_stats.get("hits", 0),
            total=hits_stats.get("total", 0),
            hit_ratio=hits_stats.get("hit_ratio", 0),
        )

    async def invalidate_key(self, key: str) -> None:
        await self.cache.delete(key=key)

    async def invalidate(
        self,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        await self.invalidate_key(key=default_method_key_builder(func, *args, **kwargs))

    def cached_func(
        self,
        func: Callable[P, Awaitable[RetType]],
        noself: bool,
        ttl: int | None = None,
        key_builder: Callable[..., str] = default_method_key_builder,
    ) -> Callable[P, Awaitable[RetType]]:
        if not ttl:
            ttl = self._default_ttl

        return CustomSingleCached(
            alias=self._alias,
            ttl=ttl,
            key_builder=key_builder,
            noself=noself,
            debug=self.debug,
        )(func)  # type: ignore

    def cached_multi_func(
        self,
        keys_kwarg: str,
        func: Callable[P, Awaitable[RetType]],
        ttl: int | None,
        noself: bool,
        key_builder: Callable[..., str] = default_method_key_builder,
    ) -> Callable[P, Awaitable[RetType]]:
        if not ttl:
            ttl = self._default_ttl

        return CustomMultiCached(
            keys_from_attr=keys_kwarg,
            alias=self._alias,
            ttl=ttl,
            key_builder=key_builder,
            noself=noself,
            debug=self.debug,
        )(func)  # type: ignore
