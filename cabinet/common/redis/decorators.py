from aioredis import ConnectionClosedError
from typing import Any, Callable, Coroutine


def avoid_disconnect(method: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
    """
    Restores connection in case of ConnectionClosedError
    """

    async def decorated(self: Any, *args: list[Any], **kwargs: dict[str, Any]) -> Any:
        try:
            result: Any = await method(self, *args, **kwargs)
        except ConnectionClosedError:
            await self.connect()
            result: Any = await method(self, *args, **kwargs)
        return result

    return decorated
