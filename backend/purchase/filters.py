from django.db.models import F
from django_filters import CharFilter, BooleanFilter
from graphene_django.filter.filterset import GlobalIDFilter, GrapheneFilterSetMixin
from common.filters import FacetFilterSet
from .models import PurchaseType, PurchaseTypeCategory


class PurchaseFilterSet(GrapheneFilterSetMixin, FacetFilterSet):
    """
    Фильтр способов покупки
    """

    city = GlobalIDFilter(field_name="city", label="Фильтр по городу")
    category = CharFilter(field_name="category__slug", label="Фильтр по категории")
    is_commercial = BooleanFilter(field_name="is_commercial", label="Фильтр по коммерции")

    category.specs = "get_category_specs"
    category.aggregate_method = "get_category_aggregate"

    @staticmethod
    def get_category_specs(queryset):
        qs = (
            queryset.annotate(label=F("category__name"), value=F("category__slug"))
            .values("label", "value")
            .order_by("category__order", "category__id")
            .distinct("category__order", "category__id")
        )
        specs = [{"label": i["label"], "value": i["value"]} for i in qs]
        return specs

    @staticmethod
    def get_category_aggregate(queryset):
        aggregate = (
            queryset.order_by("category__order", "category__id")
            .distinct("category__order", "category__id")
            .values_list("category__slug", flat=True)
        )
        return aggregate

    class Meta:
        model = PurchaseType
        fields = ("city", "category")


class PurchaseTypeCategoryFilterSet(GrapheneFilterSetMixin, FacetFilterSet):
    """
    Фильтр категорий способов покупки
    """

    city = GlobalIDFilter(field_name="purchasetype__city", label="Фильтр по городу")

    class Meta:
        model = PurchaseTypeCategory
        fields = ("city",)
