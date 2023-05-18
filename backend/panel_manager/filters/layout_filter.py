from django_filters.rest_framework import OrderingFilter
from django_filters import rest_framework as filters
from common.filters import FacetFilterSet, NumberInFilter
from properties.models import Layout


class LayoutFilter(FacetFilterSet):
    order = OrderingFilter(
        fields=("area", "price"), field_labels={"area": "Площадь", "price": "Цена"}
    )

    class Meta:
        model = Layout
        fields = ()
