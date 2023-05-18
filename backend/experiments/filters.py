from graphene_django.filter.filterset import GrapheneFilterSetMixin, GlobalIDFilter
from common.filters import FacetFilterSet
from .models import Experiment


class ExperimentFilter(GrapheneFilterSetMixin, FacetFilterSet):
    """
    Фильтр по попап тегу и городу
    """

    class Meta:
        model = Experiment
        fields = ("tag", "name")
