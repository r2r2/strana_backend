from typing import Any

from django_filters import Filter, CharFilter
from common.filters import FacetFilterSet, CharInFilter
from news.models import News

from ..models import Progress
from ..models import Camera
from ..const import ProgressMonth, ProgressQuarter
from ..querysets import ProgressQuerySet


class ProgressFilter(FacetFilterSet):
    """
    Фильтр ходов строительства
    """

    date = Filter(method="filter_date", label="Фильтр по дате")
    projects = CharInFilter(field_name="projects__slug", label="Фильтр по проекту")
    year = CharFilter(label="Фильтр по году")
    year.specs = "year_specs"
    month = CharFilter(label="Фильтр по месяцу")
    month.specs = "month_specs"
    month.aggregate_method = "month_facet"
    quarter = CharFilter(label="Фильтр по кварталу")
    quarter.specs = "quarter_specs"
    buildings = CharInFilter(label="Фильтр по корпусу", field_name="newsslide__building")

    date.specs = "get_date_specs"
    date.aggregate_method = "get_date_aggregate"

    projects.specs = "get_projects_specs"

    @staticmethod
    def year_specs(queryset: ProgressQuerySet) -> list[dict[str, Any]]:
        qs: ProgressQuerySet = (
            queryset.filter(quarter__isnull=False, year__isnull=False)
            .values_list("year", flat=True)
            .order_by("year")
            .distinct("year")
        )
        specs = [{"value": year, "label": year} for year in qs]
        return specs

    @staticmethod
    def month_specs(queryset: ProgressQuerySet) -> list[dict[str, Any]]:
        qs: ProgressQuerySet = (
            queryset.filter(month__isnull=False, year__isnull=False)
            .values_list("month", flat=True)
            .order_by("month")
            .distinct("month")
        )
        specs = []
        for i in ProgressMonth.choices:
            if i[0] in qs:
                specs.append({"value": i[0], "label": i[1]})
        return specs

    @staticmethod
    def month_facet(queryset: ProgressQuerySet) -> list[dict[str, Any]]:
        qs: ProgressQuerySet = (
            queryset.filter(month__isnull=False, year__isnull=False)
            .values_list("month", flat=True)
            .order_by("month")
            .distinct("month")
        )
        specs = []
        for i in ProgressMonth.choices:
            if i[0] in qs:
                specs.append({"value": i[0], "label": i[1]})
        return specs

    @staticmethod
    def quarter_specs(queryset: ProgressQuerySet) -> list[dict[str, Any]]:
        qs: ProgressQuerySet = (
            queryset.filter(month__isnull=False, year__isnull=False)
            .values_list("quarter", flat=True)
            .order_by("quarter")
            .distinct("quarter")
        )
        l = {i[1]: i[0] for i in ProgressQuarter.choices}
        specs = [{"value": l[quarter], "label": quarter} for quarter in qs]
        return specs

    @staticmethod
    def filter_date(queryset: ProgressQuerySet, name: str, value: Any) -> ProgressQuerySet:
        components: list[Any] = value.split("-")
        if len(components) != 2:
            qs: ProgressQuerySet = queryset
        else:
            quarter, year = components[1], components[0]
            try:
                quarter = quarter
                year: int = int(year)
                if not quarter in ["I", "II", "III", "IV"]:
                    qs: ProgressQuerySet = queryset
                else:
                    qs: ProgressQuerySet = queryset.filter(quarter=quarter, year=year)
            except ValueError:
                qs: ProgressQuerySet = queryset
        return qs

    @staticmethod
    def get_date_specs(queryset: ProgressQuerySet) -> list[dict[str, Any]]:
        qs: ProgressQuerySet = (
            queryset.filter(quarter__isnull=False, year__isnull=False)
            .values_list("quarter", "year")
            .order_by("-year", "-quarter")
            .distinct("year", "quarter")
        )
        specs: list[dict[str, Any]] = [
            {"value": f"{date[1]}-{date[0]}", "label": f"{date[0]} кв. {date[1]}"} for date in qs
        ]
        return specs

    @staticmethod
    def get_date_aggregate(queryset: ProgressQuerySet) -> list[str]:
        qs: ProgressQuerySet = (
            queryset.filter(quarter__isnull=False, year__isnull=False)
            .values_list("quarter", "year")
            .order_by("quarter", "year")
            .distinct("quarter", "year")
        )
        aggregate: list[str] = [f"{date[1]}-{date[0]}" for date in qs]
        return aggregate

    @staticmethod
    def get_projects_specs(queryset: ProgressQuerySet) -> list[dict[str, Any]]:
        qs: ProgressQuerySet = (
            queryset.filter(projects__isnull=False)
            .values_list("projects__slug", "projects__name")
            .order_by("projects__slug", "projects__name")
            .distinct("projects__slug", "projects__name")
        )
        specs: list[dict[str, Any]] = [{"value": project[0], "label": project[1]} for project in qs]
        return specs

    class Meta:
        model = News
        fields = ("projects", "date")


class CameraFilter(FacetFilterSet):
    """
    Фильтр камер
    """

    project = CharInFilter(field_name="project__slug", label="Фильтр по проекту")

    class Meta:
        model = Camera
        fields = ("project",)
