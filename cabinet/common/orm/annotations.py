from typing import Optional, Type, Any

from tortoise import Model
from tortoise.expressions import F, Subquery, Q
from tortoise.functions import Count, Max, Sum, Min, Avg, Trim, Coalesce
from tortoise.queryset import AwaitableQuery

from ..tortoise import OuterRef, Exists, SCount


class AnnotationBuilder(object):
    """
    Annotations builder based on primitive data structures
    """

    def __init__(self, model: Type[Model]) -> None:
        self.model: Type[Model] = model

    def build_f(self, field: Optional[str] = None) -> F:
        return F(field, field)

    def build_outer(self, field: Optional[str] = None) -> OuterRef:
        return OuterRef(field, field, self.model.Meta.table)

    def build_exists(self, queryset: AwaitableQuery) -> Exists:
        return Exists(queryset)

    def build_subquery(self, queryset: AwaitableQuery) -> Subquery:
        return Subquery(queryset)

    def build_min(self, field: Optional[str], filter: Optional[Q] = None) -> Min:
        return Min(field, _filter=filter)

    def build_sum(self, field: Optional[str] = None, filter: Optional[Q] = None) -> Sum:
        return Sum(field, _filter=filter)

    def build_max(self, field: Optional[str] = None, filter: Optional[Q] = None) -> Max:
        return Max(field, _filter=filter)

    def build_avg(self, field: Optional[str] = None, filter: Optional[Q] = None) -> Avg:
        return Avg(field, _filter=filter)

    def build_count(self, field: Optional[str] = None, filter: Optional[Q] = None) -> Count:
        return Count(field, _filter=filter)

    def build_scount(
        self, queryset: AwaitableQuery, filters: Optional[dict[str, Any]] = None
    ) -> Subquery:
        return SCount(queryset, filters=filters)

    def build_trim(self, field: Optional[str] = None) -> Trim:
        return Trim(field)

    def build_coalsce(self, field: str, default_value: Any) -> Coalesce:
        return Coalesce(field, default_value)
