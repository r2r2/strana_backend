from graphene_django.filter.filterset import GrapheneFilterSetMixin, GlobalIDFilter
from common.filters import FacetFilterSet
from .models import PopUpInfo, PopUpTag


class PopUpInfoFilter(GrapheneFilterSetMixin, FacetFilterSet):
    """
    Фильтр по попап тегу и городу
    """
    project = GlobalIDFilter(field_name="project__slug", label="Фильтр по проекту")

    class Meta:
        model = PopUpInfo
        fields = ("city", "pop_up_tag__tag", "project")


class PopUpTagFilter(GrapheneFilterSetMixin, FacetFilterSet):
    """
    Фильтр по попап тегу и городу
    """

    class Meta:
        model = PopUpTag
        fields = ("tag", )
