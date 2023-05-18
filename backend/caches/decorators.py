from typing import Callable
from graphene.utils.str_converters import to_camel_case
from .storages import query_storage


def cached_resolver(**options) -> Callable:
    """
    Добавляет резолвер в список кэширования
    :variables: использовать переменные
    :user_agent: использовать ЮА
    :domain: использовать домен
    :crontab: использовать кронтаб
    :time: время кэширования
    """

    def decorator(resolver) -> Callable:
        resolver_name = resolver.__name__.split("_")
        resolver_name.pop(0)
        query_name = to_camel_case("_".join(resolver_name))
        query_storage.add(query_name, options)
        return resolver

    return decorator
