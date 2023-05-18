from django.db.models import F
from django_filters import BooleanFilter
from graphene_django.filter.filterset import GlobalIDFilter, GrapheneFilterSetMixin
from graphql_relay import to_global_id
from cities.schema import CityType
from common.filters import FacetFilterSet
from .models import Office


class OfficeFilterSet(GrapheneFilterSetMixin, FacetFilterSet):
    """
    Фильтр офисов
    """

    city = GlobalIDFilter(field_name="cities", label="Фильтр по городам")
    project = GlobalIDFilter(field_name="projects__slug", label="Фильтр по проекту")
    is_central = BooleanFilter(field_name="is_central", label="Фильтр по центральному")

    city.specs = "get_city_specs"
    project.skip = True

    class Meta:
        model = Office
        fields = ("city", "project", "is_central")

    @staticmethod
    def get_city_specs(queryset):
        res = (
            queryset.annotate(label=F("cities__name"), value=F("cities__id"))
            .values("label", "value")
            .order_by("cities__id")
            .distinct("cities__id")
        )
        return [
            {"label": i["label"], "value": to_global_id(CityType.__name__, i["value"])} for i in res
        ]
