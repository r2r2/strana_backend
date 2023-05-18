from django_filters import BaseInFilter

from buildings.models import Floor
from common.filters import FacetFilterSet


class FloorFilter(FacetFilterSet):
    section = BaseInFilter(label="Фильтр по секции")

    class Meta:
        model = Floor
        fields = ()
