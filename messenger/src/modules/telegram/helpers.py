import asyncio
import time
from functools import wraps
from typing import Awaitable, Callable, ParamSpec, Sequence, TypeVar

P = ParamSpec("P")
T = TypeVar("T")


def escape_markdown_v2(text: str, keep_chars: Sequence[str] | None = None) -> str:
    escaped_chars = {"_", "*", "[", "]", "(", ")", "~", "`", ">", "#", "+", "-", "=", "|", "{", "}", ".", "!"}
    if keep_chars:
        escaped_chars = escaped_chars.difference(keep_chars)

    for char in escaped_chars:
        text = text.replace(char, f"\\{char}")

    return text


def throttled(rps: int) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:  # noqa: TAE002
    delay_between_calls = 1 / rps
    last_call = None

    def _inner(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            nonlocal last_call

            time_now = time.monotonic()
            if last_call and (time_diff := time_now - last_call) < delay_between_calls:
                await asyncio.sleep(delay_between_calls - time_diff)

            result = await func(*args, **kwargs)
            last_call = time.monotonic()
            return result  # noqa

        return wrapper

    return _inner
