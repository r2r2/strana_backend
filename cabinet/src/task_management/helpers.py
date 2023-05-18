from enum import Enum
from typing import Callable, Any


class _CacheSlugValues:
    """
    Кэширование значений слагов
    """
    cache: dict[str: list[str]] = {}

    def __init__(self, func: Callable[..., Any]):
        self.func = func

    def __call__(self, *string: str) -> list[str]:
        if string in self.cache:
            return self.cache[string]
        else:
            list_slugs = self.func(*string)
            self.cache[string] = list_slugs
            return list_slugs


class Slugs(Enum):
    @classmethod
    @_CacheSlugValues
    def get_slug_values(cls, slug: str) -> list[str]:
        """
        Получение всех значений нужного класса слагов по переданному значению слага
        """
        for enum_cls in cls.__subclasses__():
            slug_values = [s.value for s in enum_cls]
            if slug in slug_values:
                return slug_values
