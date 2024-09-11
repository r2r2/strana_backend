from typing import Any
from unittest.mock import Mock

import pytest
from cachetools import Cache, LFUCache, LRUCache, TTLCache

from src.core.common.caching import cached_method
from src.core.common.memory_cache import InMemoryCacher


@pytest.mark.parametrize(
    ["cache_impl", "maxsize"],
    [
        [TTLCache(maxsize=10, ttl=120), 10],
        [LRUCache(maxsize=10), 10],
        [LFUCache(maxsize=10), 10],
        [LFUCache(maxsize=100), 100],
    ],
)
@pytest.mark.unit
async def test_simple(cache_impl: Cache[str, Any], maxsize: int) -> None:
    class _Test:
        def __init__(self) -> None:
            self._cache = InMemoryCacher(cache=cache_impl)
            self._trigger = Mock()

        @cached_method(cacher_location="_cache")
        async def cached_async_method(self, x: int) -> int:
            self._trigger()
            return x

    t = _Test()
    assert await t.cached_async_method(1) == 1
    assert await t.cached_async_method(1) == 1
    assert t._trigger.call_count == 1

    for i in range(maxsize):
        assert await t.cached_async_method(i + maxsize) == i + maxsize
        assert await t.cached_async_method(i + maxsize) == i + maxsize

    assert t._trigger.call_count == 1 + maxsize
    assert t._cache.get_statistics()
