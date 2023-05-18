import traceback
from asyncio import Future, Task
from json import dumps
from typing import Any, Callable, Coroutine, Generator, Optional, Union

from tortoise import Model

from .entities import BaseBookingCase, BaseBookingService
from .exceptions import BookingUnknownReasonError


def logged_action(
    content: Optional[str] = None,
) -> Callable[[Callable[..., Coroutine]], Callable[..., Coroutine]]:
    """
    Логирует элементы бизнес логики определенные в отдельных методах
    """

    def decorator(method: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
        if method.__name__.count("__call__"):
            decorated: Callable[..., Coroutine] = method
        else:

            async def decorated(
                self: Union[BaseBookingCase, BaseBookingService], booking: Model, *args, **kwargs,
            ) -> Any:
                log_generator: Generator = self.generate_log(
                    content=content, booking_before=booking, use_case=self.__class__.__name__
                )
                next(log_generator)
                try:
                    result: Any = await method(self, booking, *args, **kwargs)
                except Exception as error:
                    try:
                        tb = ''.join(traceback.format_tb(error.__traceback__))
                        error_text: str = f'{error.__class__.__name__}:{str(error)}, {tb}'
                        log_generator.send((booking, None, error_text))
                    except StopIteration:
                        pass
                    raise BookingUnknownReasonError from error
                try:
                    if isinstance(result, str):
                        log_generator.send((booking, result, None))
                    elif isinstance(result, (dict, list, tuple)):
                        log_generator.send((booking, dumps(result), None))
                    elif isinstance(result, (bool, int, float)):
                        log_generator.send((booking, str(result), None))
                    elif isinstance(result, (Future, Task)):
                        log_generator.send((booking, None, None))
                    elif result is None:
                        log_generator.send((booking, None, None))
                    else:
                        log_generator.send((booking, None, f'Unexpected result type <{type(result)}>'))
                except StopIteration:
                    pass
                return result

        decorated.__name__ = method.__name__

        return decorated

    return decorator


def logged_mutation(
    use_case: Union[BaseBookingCase, BaseBookingService], content: Optional[str] = None
) -> Callable[[Callable[..., Coroutine]], Callable[..., Coroutine]]:
    """
    Логирует элементы изменения состояния данных
    """

    def decorator(method: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
        if method.__name__.count("__call__"):
            decorated: Callable[..., Coroutine] = method
        else:

            async def decorated(*args, **kwargs) -> Model:
                booking_before: Union[Model, None] = kwargs.get("booking", None)
                log_generator: Generator = use_case.generate_log(
                    content=content,
                    booking_before=booking_before,
                    use_case=use_case.__class__.__name__,
                )
                next(log_generator)
                try:
                    booking: Model = await method(*args, **kwargs)
                except Exception as error:
                    try:
                        log_generator.send((booking_before, None, str(error)))
                    except StopIteration:
                        pass
                    raise BookingUnknownReasonError from error
                if booking:
                    try:
                        log_generator.send((booking, None, None))
                    except StopIteration:
                        pass
                return booking

        decorated.__name__ = method.__name__

        return decorated

    return decorator
