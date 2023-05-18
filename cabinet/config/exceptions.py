from collections import OrderedDict
from typing import Any, Callable, Type


def get_exceptions() -> OrderedDict[Type[Exception], Callable[..., Any]]:
    from common import handlers as common_handlers
    from src.users import exceptions as users_exceptions
    from src.booking import exceptions as booking_exceptions
    from src.properties import exceptions as properties_exceptions
    from src.documents import exceptions as document_exceptions
    from src.agents import exceptions as agents_exceptions
    from src.represes import exceptions as represes_exceptions
    from src.agencies import exceptions as agencies_exceptions
    from src.admins import exceptions as admins_exceptions
    from src.showtimes import exceptions as showtimes_exceptions
    from common.amocrm import exceptions as amocrm_exceptions
    from src.task_management import exceptions as task_management_exceptions
    from src.meetings import exceptions as meetings_exceptions
    from src.cities import exceptions as cities_exceptions

    modules: list[Any] = [
        users_exceptions,
        agents_exceptions,
        booking_exceptions,
        document_exceptions,
        represes_exceptions,
        agencies_exceptions,
        properties_exceptions,
        admins_exceptions,
        showtimes_exceptions,
        amocrm_exceptions,
        task_management_exceptions,
        meetings_exceptions,
        cities_exceptions
    ]

    exceptions: OrderedDict[Type[Exception], Callable[..., Any]] = OrderedDict()

    for exc_module in modules:
        for _, exception in exc_module.__dict__.items():
            if isinstance(exception, type) and issubclass(exception, Exception):
                if "Base" not in exception.__name__ and "Exception" not in exception.__name__:
                    exceptions[exception]: Type[
                        Exception
                    ] = common_handlers.common_exception_handler

    return exceptions
