from typing import Union, Type, Optional, Any

from tortoise import Model
from tortoise.expressions import F
from tortoise.functions import Min, Max, Trim
from tortoise.queryset import QuerySet, QuerySetSingle, ValuesQuery

from src.users.models import CurrentUserData


class UserRepoSpecsMixin(object):
    """
    Миксин репозитория пользователя со спеками
    """

    def agent_specs(
        self,
        queryset: Union[QuerySet[Type[Model]], QuerySetSingle[Type[Model]]],
        group: Optional[str] = None,
        addition: Optional[dict[str, Any]] = None,
    ) -> ValuesQuery:
        """
        Спеки агента
        """
        if group is None:
            group: str = "id"
        filters: dict[str, Any] = dict(agent_id__isnull=False, agent_surname__isnull=False)
        if addition:
            filters.update(addition)
        specs_queryset: ValuesQuery = (
            queryset.annotate(agent_surname=Trim("agent__surname"))
            .filter(**filters)
            .order_by("agent_id", "agent_surname")
            .distinct()
            .values(value=F("agent_id"), label=F("agent_surname"))
        )
        return specs_queryset

    def work_period_specs(
        self,
        queryset: Union[QuerySet[Type[Model]], QuerySetSingle[Type[Model]]],
        group: Optional[str] = None,
        addition: Optional[dict[str, Any]] = None,
    ) -> ValuesQuery:
        """
        Спеки периода работы
        """
        if group is None:
            group: str = "id"
        filters: dict[str, Any] = dict(work_end__isnull=False, work_start__isnull=False)
        if addition:
            filters.update(addition)
        specs_queryset: ValuesQuery = (
            queryset.filter(**filters)
            .annotate(min=Min("work_start"), max=Max("work_end"))
            .group_by(group)
            .values("min", "max")
        )
        return specs_queryset


class UserRepoFacetsMixin(object):
    """
    Миксин репозитория пользователя с фасетами
    """

    def agents_facets(
        self,
        queryset: Union[QuerySet[Type[Model]], QuerySetSingle[Type[Model]]],
        group: Optional[str] = None,
    ) -> ValuesQuery:
        """
        Фасеты агента
        """
        if group is None:
            group: str = "id"
        facets_queryset: ValuesQuery = (
            queryset.filter(agent__id__isnull=False, agent__surname__isnull=False)
            .order_by("agent__id")
            .distinct()
            .values_list("agent__id", flat=True)
        )
        return facets_queryset

    def work_period_facets(
        self,
        queryset: Union[QuerySet[Type[Model]], QuerySetSingle[Type[Model]]],
        group: Optional[str] = None,
    ) -> ValuesQuery:
        """
        Фасеты периода работы
        """
        if group is None:
            group: str = "id"
        facets_queryset: ValuesQuery = (
            queryset.filter(work_end__isnull=False, work_start__isnull=False)
            .annotate(min=Min("work_start"), max=Max("work_end"))
            .group_by(group)
            .values(min=F("min"), max=F("max"))
        )
        return facets_queryset


class CurrentUserDataMixin:
    """
    Add extra user data mixin
    """
    __user_data: CurrentUserData = CurrentUserData()

    @property
    def current_user_data(self):
        """Property for private access to user_data"""
        return self.__user_data

    def init_user_data(
            self, agent_id: Optional[int] = None, agency_id: Optional[int] = None
    ) -> CurrentUserData:
        """Save user_data to class"""
        self.__user_data = CurrentUserData(agent_id=agent_id, agency_id=agency_id)
        return self.current_user_data
