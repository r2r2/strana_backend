from graphene_django.filter.filterset import GrapheneFilterSetMixin, GlobalIDFilter
from common.filters import FacetFilterSet
from .models import InfraCategory, Infra, MainInfra, SubInfra, RoundInfra


class InfraCategoryFilter(GrapheneFilterSetMixin, FacetFilterSet):
    """
    Фильтр категорий инфраструктур на карте
    """

    project = GlobalIDFilter(field_name="infra__project__slug", label="Фильтр по проекту")

    class Meta:
        model = InfraCategory
        fields = ("project",)


class InfraFilter(GrapheneFilterSetMixin, FacetFilterSet):
    """
    Фильтр инфраструктур на карте
    """

    project = GlobalIDFilter(field_name="project__slug", label="Фильтр по проекту")

    class Meta:
        model = Infra
        fields = ("project", "category")


class MainInfraFilter(GrapheneFilterSetMixin, FacetFilterSet):
    """
    Фильтр главных инфраструктур на генплане
    """

    project = GlobalIDFilter(field_name="project__slug", label="Фильтр по проекту")

    class Meta:
        model = MainInfra
        fields = ("project",)


class SubInfraFilter(GrapheneFilterSetMixin, FacetFilterSet):
    """
    Фильтр дополнительных инфраструктур на генплане
    """

    project = GlobalIDFilter(field_name="project__slug", label="Фильтр по проекту")

    class Meta:
        model = SubInfra
        fields = ("project",)


class RoundInfraFilter(GrapheneFilterSetMixin, FacetFilterSet):
    """
    Фильтр окружных инфраструктур на генплане
    """

    project = GlobalIDFilter(field_name="project__slug", label="Фильтр по проекту")

    class Meta:
        model = RoundInfra
        fields = ("project",)
