from typing import Callable, Coroutine

from ..requests import CommonResponse


def refresh_on_status(method: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
    """
    Refreshes auth based on _refresh_statuses attribute of the class
    """

    async def decorated(self, *args, **kwargs) -> CommonResponse:
        response: CommonResponse = await method(self, *args, **kwargs)
        if response.status in self._refresh_statuses:
            await self._refresh_auth()
            response: CommonResponse = await method(self, *args, **kwargs)
        return response

    decorated.__name__ = method.__name__

    return decorated
