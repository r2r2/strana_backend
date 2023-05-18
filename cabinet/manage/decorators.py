from typing import Callable, Awaitable, Any, Union

from tortoise.exceptions import IntegrityError


def skip_integrity(method: Callable[..., Awaitable]) -> Callable[..., Awaitable]:
    """
    Пропуск IntegrityError
    """

    async def decorated(*args: Any, **kwargs: Any) -> Union[Any, None]:
        try:
            result: Any = await method(*args, **kwargs)
        except IntegrityError:
            result = None
        return result

    return decorated
