from collections import OrderedDict
from typing import Any, Callable


def get_exceptions() -> OrderedDict[type[Exception], Callable[..., Any]]:
    from common import handlers as common_handlers
    from common.depreg import exceptions as depreg_exceptions
    from common.settings import exceptions as settings_exceptions
    from common.nextcloud import exceptions as nextcloud_exceptions
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
    from src.text_blocks import exceptions as text_block_exceptions
    from src.projects import exceptions as projects_exceptions
    from src.events import exceptions as event_exceptions
    from src.notifications import exceptions as notifications_exceptions
    from src.additional_services import exceptions as additional_service_exceptions
    from src.events_list import exceptions as events_list_exceptions
    from src.commercial_offers import exceptions as commercial_offers_exceptions
    from src.news import exceptions as news_exceptions
    from common.tilda import exceptions as tilda_exceptions
    from src.mortgage import exceptions as mortgage_exceptions
    from src.questionnaire import exceptions as questionnaire_exceptions

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
        cities_exceptions,
        text_block_exceptions,
        projects_exceptions,
        event_exceptions,
        notifications_exceptions,
        additional_service_exceptions,
        events_list_exceptions,
        depreg_exceptions,
        commercial_offers_exceptions,
        tilda_exceptions,
        settings_exceptions,
        news_exceptions,
        mortgage_exceptions,
        questionnaire_exceptions,
        nextcloud_exceptions,
    ]

    exceptions: OrderedDict[type[Exception], Callable[..., Any]] = OrderedDict()

    for exc_module in modules:
        for _, exception in exc_module.__dict__.items():
            if isinstance(exception, type) and issubclass(exception, Exception):
                if "Base" not in exception.__name__ and "Exception" not in exception.__name__:
                    exceptions[exception]: type[
                        Exception
                    ] = common_handlers.common_exception_handler

    return exceptions
