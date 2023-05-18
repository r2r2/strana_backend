from django_filters import BaseInFilter

from buildings.models import GroupSection
from common.filters import FacetFilterSet


class GroupSectionFilter(FacetFilterSet):
    building = BaseInFilter(label="Фильтр по корпусу")

    class Meta:
        model = GroupSection
        fields = ()
