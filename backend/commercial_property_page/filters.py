from graphene_django.filter import GlobalIDFilter
from graphene_django.filter.filterset import GrapheneFilterSetMixin
from common.filters import FacetFilterSet
from .models import CommercialPropertyPage


class CommercialPropertyPageFilterSet(GrapheneFilterSetMixin, FacetFilterSet):
    """
    Фильтр страницы коммерческой недвижимости
    """

    city = GlobalIDFilter(field_name="city", label="Фильтр по городу")

    class Meta:
        model = CommercialPropertyPage
        fields = ("city",)
