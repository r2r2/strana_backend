from typing import Any
from common.unleash.cache import RCache


def redis_lock(lock_id):
    cache = RCache()
    result: Any = cache.get(lock_id)
    if result is None:
        cache.set(key=lock_id, value=lock_id, expire=60*10)
        return not bool(result)
    return not bool(result)
