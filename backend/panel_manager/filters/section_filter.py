from django_filters import BaseInFilter

from buildings.models import Section
from common.filters import FacetFilterSet


class SectionFilter(FacetFilterSet):
    group = BaseInFilter(label="Фильтр по группе секций")
    building = BaseInFilter(label="Фильтр по корпусу")

    class Meta:
        model = Section
        fields = ()
