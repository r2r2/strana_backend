from copy import copy
from django.db.models import Case, When, CharField, Value, Q
from django_filters import CharFilter, Filter
from graphene_django.filter.filterset import GrapheneFilterSetMixin, GlobalIDMultipleChoiceFilter
from graphql_relay import to_global_id
from cities.schema import CityType
from common.filters import FacetFilterSet
from projects.models import Project
from .constants import ProjectStatusType


class ProjectFacetFilterSet(FacetFilterSet):
    """
    Фильтр для проекта с подсчетом недвижимости по типу
    """

    def facets(self):
        qs = copy(self.qs)
        count_residential = qs.filter(is_residential=True).count()
        count_commercial = qs.filter(is_commercial=True).count()
        # статусы для глобальных проектов
        count_current = qs.filter(status=ProjectStatusType.CURRENT).count()
        count_completed = qs.filter(status=ProjectStatusType.COMPLETED).count()
        count_future = qs.filter(status=ProjectStatusType.FUTURE).count()
        res = super().facets()
        res["count_residential"] = count_residential
        res["count_commercial"] = count_commercial
        res["count_current"] = count_current
        res["count_completed"] = count_completed
        res["count_future"] = count_future
        return res


class ProjectFilterSet(GrapheneFilterSetMixin, ProjectFacetFilterSet):
    """
    Фильтр проекта
    """

    slug = CharFilter(field_name="slug", label="Фильтр по слагу")
    kind = Filter(method="filter_kind", label="Фильтр по типу")

    slug.specs = "get_slug_specs"
    kind.specs = "get_kind_specs"

    slug.aggregate_method = "get_slug_aggregate"
    kind.aggregate_method = "get_kind_aggregate"

    status = CharFilter(
        field_name="status", method="filter_status", label="Фильтр по статусу проекта"
    )
    status.specs = "get_status_specs"
    status.aggregate_method = "get_status_aggregate"

    @staticmethod
    def filter_status(queryset, name, value):
        q = Q(status=value)
        return queryset.filter(q)

    @staticmethod
    def get_status_specs(queryset):
        statuses = queryset.values_list("status", flat=True).order_by("status").distinct("status")
        choices = dict(ProjectStatusType.choices)
        return [{"label": choices.get(st), "value": st} for st in statuses]

    @staticmethod
    def get_status_aggregate(queryset):
        return queryset.values_list("status", flat=True).order_by("status").distinct("status")

    @staticmethod
    def filter_kind(queryset, name, value):
        if value:
            if value == "commercial":
                return queryset.filter(is_commercial=True)
            elif value == "residential":
                return queryset.filter(is_residential=True)
        return queryset

    @staticmethod
    def get_slug_specs(queryset):
        res = queryset.values("name", "slug").order_by("order", "id").distinct("order", "id")
        specs = [{"label": i["name"], "value": i["slug"]} for i in res]
        return specs

    @staticmethod
    def get_kind_specs(queryset):
        res = (
            queryset.annotate(
                label=Case(
                    When(is_commercial=True, then=Value("Коммерческие")),
                    When(is_residential=True, then=Value("Жилые")),
                    output_field=CharField(),
                ),
                value=Case(
                    When(is_commercial=True, then=Value("commercial")),
                    When(is_residential=True, then=Value("residential")),
                    output_field=CharField(),
                ),
            )
            .filter(label__isnull=False, value__isnull=False)
            .values("label", "value")
            .order_by("label", "value")
            .distinct("label", "value")
        )
        specs = [{"label": i["label"], "value": i["value"]} for i in res]
        return specs

    @staticmethod
    def get_slug_aggregate(queryset):
        aggregate = (
            queryset.order_by("order", "id").distinct("order", "id").values_list("slug", flat=True)
        )
        return aggregate

    @staticmethod
    def get_kind_aggregate(queryset):
        aggregate = (
            queryset.annotate(
                value=Case(
                    When(is_commercial=True, then=Value("commercial")),
                    When(is_residential=True, then=Value("residential")),
                    output_field=CharField(),
                )
            )
            .filter(value__isnull=False)
            .order_by("value")
            .distinct("value")
            .values_list("value", flat=True)
        )
        return aggregate

    class Meta:
        model = Project
        fields = ("id", "slug")


class GlobalProjectFilterSet(ProjectFilterSet):
    """
    Фильтр глобального проекта
    """

    city = GlobalIDMultipleChoiceFilter(field_name="city__id", label="Фильтр по городу")

    city.specs = "get_city_specs"
    city.aggregate_method = "get_city_aggregate"

    @staticmethod
    def get_city_specs(queryset):
        res = (
            queryset.values("city__order", "city__id", "city__name")
            .order_by("city__order", "city__id", "city__name")
            .distinct("city__order", "city__id", "city__name")
        )
        specs = [
            {"label": i["city__name"], "value": to_global_id(CityType.__name__, i["city__id"])}
            for i in res
        ]

        return specs

    @staticmethod
    def get_city_aggregate(queryset):
        res = queryset.order_by("city__id").distinct("city__id").values_list("city__id", flat=True)
        aggregate = [to_global_id(CityType.__name__, i) for i in res]
        return aggregate

    class Meta:
        model = Project
        fields = ("id", "slug", "city", "status", "name")
