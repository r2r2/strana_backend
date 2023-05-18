from tortoise import Model
from tortoise.query_utils import Q
from typing import Any, Optional, Type, Union


FilterType = Union[Q, dict[str, Any]]


class QBuilder(object):
    """
    Q object builder based on primitive data structures
    """

    def __init__(self, model: Type[Model]) -> None:
        self.model: Type[Model] = model

    def __call__(
        self,
        or_filters: Optional[list[FilterType]] = None,
        and_filters: Optional[list[FilterType]] = None,
    ) -> Q:
        filter = Q()
        if or_filters is not None:
            for or_filter in or_filters:
                if isinstance(or_filter, Q):
                    filter |= or_filter
                else:
                    filter |= Q(**or_filter)
        elif and_filters is not None:
            for and_filter in and_filters:
                if isinstance(and_filter, Q):
                    filter &= and_filter
                else:
                    filter &= Q(**and_filter)
        return filter
