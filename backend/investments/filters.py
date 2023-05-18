from graphene_django.filter.filterset import GrapheneFilterSetMixin, GlobalIDFilter
from common.filters import FacetFilterSet
from .models import YieldComparison, InvestmentTypes, RentalBusinessSales


class YieldComparisonFilter(GrapheneFilterSetMixin, FacetFilterSet):
    """
    Фильтр по сравнению доходности
    """

    class Meta:
        model = YieldComparison
        fields = ("rent", )


class InvestmentTypesFilter(GrapheneFilterSetMixin, FacetFilterSet):
    """
    Фильтр по сравнению видов инвестиций
    """

    class Meta:
        model = InvestmentTypes
        fields = ("investment_types", )


class RentalBusinessSalesFilter(GrapheneFilterSetMixin, FacetFilterSet):
    """
    Фильтр по кейсам продаж арендного бизнеса
    """

    class Meta:
        model = RentalBusinessSales
        fields = ("price", )
