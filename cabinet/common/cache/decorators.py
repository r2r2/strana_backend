from typing import Any, Callable, Coroutine
from hashlib import md5

from .storages import CacheStorage


def cache_storage(method: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
    """
    Cache response data
    """
    async def decorated(self, *args: list[Any], **kwargs: dict[str, Any]) -> Any:
        storage: CacheStorage = await CacheStorage()
        key = tuple(map(str, (method.__name__,) + args + tuple(kwargs.values())))
        storage_key = f"method_cache_{md5(''.join(key).encode()).hexdigest()}"
        result: Any = await storage.get(storage_key)
        if result is None:
            result: Any = await method(self, *args, **kwargs)
            await storage.set(key=storage_key, value=result, expire=3_600)
        return result

    return decorated
