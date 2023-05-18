from django_filters import BaseInFilter

from buildings.models import Building
from common.filters import FacetFilterSet


class BuildingFilter(FacetFilterSet):
    project = BaseInFilter(label="Фильтр по проектам")

    class Meta:
        model = Building
        fields = ()
