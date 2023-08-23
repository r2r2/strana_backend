from typing import Any, Optional, Union
from config import session_config

from ..wrappers import mark_async
from ..redis import broker as redis, Redis


@mark_async
class CacheStorage(object):
    """
    Storage of session data
    """

    async def __ainit__(self, broker: Optional[Any] = None) -> None:
        self.redis: Redis = redis
        if broker:
            self.redis: Redis = broker

        self.expire: int = session_config["expire"]

    async def set(self, key: Union[str, int, bytes, bytearray], value: Any, expire: int = None) -> bool:
        """
        Set value to session storage by key
        """
        expire: int = expire or self.expire
        ok: bool = await self.redis.set(key=key, value=value, expire=expire)
        if not ok:
            self.data.pop(key)
        return ok

    async def get(self, key: Union[str, int, bytes, bytearray], default: Optional[Any] = None) -> Any:
        """
        Get value from session storage by key
        """
        value: dict[str, Any] = await self.redis.get(key=key)
        if value is None:
            value: Any = default
        return value

