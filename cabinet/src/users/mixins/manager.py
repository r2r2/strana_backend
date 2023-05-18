from typing import Union, Type, Optional, Any

from tortoise import Model
from tortoise.expressions import F
from tortoise.functions import Min, Max, Trim
from tortoise.queryset import QuerySet, QuerySetSingle, ValuesQuery, ValuesListQuery


class ManagerRepoFacetsMixin(object):
    """
    Миксин репозитория менеджера с фасетами
    """

    def cities_facets(
        self,
        queryset: Union[QuerySet[Type[Model]], QuerySetSingle[Type[Model]]],
    ) -> ValuesListQuery:
        """
        Фасеты города
        """
        facets_queryset: ValuesListQuery = (
            queryset.filter(city__in=[])
        )
        return facets_queryset
