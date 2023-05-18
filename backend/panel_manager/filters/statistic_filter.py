from common.filters import FacetFilterSet

from ..models import Statistic


class StatisticFilter(FacetFilterSet):
    class Meta:
        model = Statistic
        fields = ("metting", "slide")
