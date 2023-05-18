from __future__ import annotations
from django.db.models import QuerySet


class OfficeQuerySet(QuerySet):
    """
    Менеджер офисов
    """

    def filter_active(self) -> OfficeQuerySet:
        return self.filter(active=True, cities__active=True).distinct()
