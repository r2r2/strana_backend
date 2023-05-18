from collections.abc import Iterable
from json import dumps, loads

from config import redis_config
from typing import Any, Union, Optional
from aioredis import RedisConnection, create_connection, ReplyError

from .decorators import avoid_disconnect


class Redis(object):
    """
    Redis service
    """

    def __init__(self) -> None:
        self._address: str = redis_config["address"]
        self._connection: RedisConnection = None

    async def connect(self) -> None:
        """
        Create connection on application startup
        """
        self._connection: RedisConnection = await create_connection(self._address)

    @avoid_disconnect
    async def flush(self) -> None:
        await self._connection.execute(b"FLUSHALL")

    @avoid_disconnect
    async def all(self) -> Union[str, dict[str, Any], None]:
        result: list[bytes] = await self._connection.execute(b"KEYS", "*")
        if result is not None:
            result: list[str] = [res.decode("utf-8") for res in result]
        return result

    @avoid_disconnect
    async def get(self, key: str) -> Union[str, dict[str, Any], None]:
        """
        Get item from redis
        """
        result: bytes = await self._connection.execute(b"GET", key)
        if result is not None:
            result: str = result.decode("utf-8")
            try:
                result: Union[list[Any], dict[str, Any]] = loads(result)
            except ValueError:
                result: str = result
        return result

    @avoid_disconnect
    async def lget(self, key: str, start: Optional[int] = 0, end: Optional[int] = -1) -> list[Any]:
        """
        Get list item from redis
        """
        try:
            result: list[bytes] = await self._connection.execute(b"LRANGE", key, start, end)
            if result is not None:
                result: list[Any] = list(map(lambda x: x.decode("utf-8"), result))
        except ReplyError:
            result: Union[str, dict[str, Any], None] = await self.get(key)
        return result

    @avoid_disconnect
    async def append(self, key: str, value: Any) -> bool:
        """
        Append item to list-like key storage
        """
        if isinstance(value, Iterable):
            value: str = " ".join(
                list(str(v) for v in list(filter(lambda x: x is not None, value)))
            )
        print(value)
        result: bytes = await self._connection.execute(b"LPUSH", key, value)
        ok: bool = result.decode("utf-8") == "OK" if isinstance(result, bytes) else bool(result)
        return ok

    @avoid_disconnect
    async def set(
        self,
        key: str,
        value: Union[str, dict[str, Any], list[Any]],
        expire: Optional[Union[int, str]] = 2_147_483_647,
    ) -> bool:
        """
        Set item to redis
        """
        if isinstance(value, dict) or isinstance(value, list):
            try:
                result: bytes = await self._connection.execute(
                    b"SET", key, dumps(value), b"EX", expire
                )
                ok: bool = result.decode("utf-8") == "OK"
            except ValueError:
                ok: bool = False
        else:
            result: bytes = await self._connection.execute(b"SET", key, value, b"EX", expire)
            ok: bool = result.decode("utf-8") == "OK"
        return ok

    @avoid_disconnect
    async def delete(self, key: str) -> bool:
        """
        Delete item from redis
        """
        await self._connection.execute(b"DEL", key)
        return True

    async def disconnect(self) -> None:
        """
        Remove connection on application shutdown
        """
        self._connection.close()
        await self._connection.wait_closed()


broker: Redis = Redis()
