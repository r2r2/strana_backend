from django.db.models import F, Q, Count, Case, When, Value, CharField
from django_filters import Filter, OrderingFilter, BooleanFilter
from graphene_django.filter import GlobalIDFilter
from graphene_django.filter.filterset import GrapheneFilterSetMixin
from graphql_relay import to_global_id
from cities.schema import CityType
from .constants import NewsType
from .models import News
from common.filters import FacetFilterSet, ListInFilter
from projects.schema import ProjectType


class BaseNewsFilter(GrapheneFilterSetMixin, FacetFilterSet):
    """
    Базовый фильтр новостей
    """

    project = GlobalIDFilter(field_name="projects__slug", label="Фильтр по проекту")

    project.specs = "get_project_specs"
    project.aggregate_method = "project_aggregate"

    order = OrderingFilter(
        fields=(("order", "order"), ("start", "start"), ("end", "end"), ("date", "date"))
    )
    order.skip = True

    class Meta:
        model = News
        fields = ("project",)

    @staticmethod
    def project_aggregate(queryset):
        res = (
            queryset.filter(projects__slug__isnull=False)
            .order_by()
            .values_list("projects__slug", flat=True)
            .distinct()
        )
        aggregate = [to_global_id(ProjectType.__name__, elem) for elem in res]
        return aggregate

    @staticmethod
    def get_project_specs(queryset):
        res = (
            queryset.filter(projects__slug__isnull=False)
            .annotate(label=F("projects__name"), value=F("projects__slug"))
            .values("label", "value")
            .order_by("projects__order", "projects__id")
            .distinct("projects__order", "projects__id")
        )
        specs = [
            {"label": i["label"], "value": to_global_id(ProjectType.__name__, i["value"])}
            for i in res
        ]
        return specs


class ProgressFilterSet(BaseNewsFilter):
    """
    Фильтр ходов строительства
    """

    date = Filter(method="date_filter", label="Фильтр по дате")
    date.specs = "date_specs"
    date.aggregate_method = "date_aggregate"

    class Meta:
        model = News
        fields = ("project", "date")

    @staticmethod
    def date_filter(queryset, name, value):
        parts = value.split("-")
        if len(parts) != 2:
            return queryset
        return queryset.filter(quarter=parts[0], date__year=parts[1])

    @staticmethod
    def date_specs(queryset):
        dates = (
            queryset.filter(date__isnull=False, quarter__isnull=False)
            .order_by("-date__year", "-quarter")
            .distinct("date__year", "quarter")
            .values("date__year", "quarter")
        )
        specs = [
            {
                "label": f"{date['quarter']} кв. {date['date__year']}",
                "value": f"{date['quarter']}-{date['date__year']}",
            }
            for date in dates
        ]
        return specs

    @staticmethod
    def date_aggregate(queryset):
        dates = (
            queryset.filter(date__isnull=False, quarter__isnull=False)
            .order_by("-date__year", "-quarter")
            .distinct("date__year", "quarter")
            .values("date__year", "quarter")
        )
        aggregate = [f"{date['quarter']}-{date['date__year']}" for date in dates]
        return aggregate


class NewsFilterSet(BaseNewsFilter):
    """
    Фильтр новостей
    """

    type = ListInFilter(method="type_filter", label="Фильтр по типу")
    projectsKind = Filter(method="filter_projects_kind", label="Фильтр по типу проекта")
    projectsCity = GlobalIDFilter(field_name="projects__city__id", label="Фильтр по городу")
    is_display_flat_listing = BooleanFilter(field_name="is_display_flat_listing")
    is_display_flat_listing.skip = True

    type.specs = "get_type_specs"
    type.aggregate_method = "type_aggregate"

    projectsKind.specs = "get_projects_kind_specs"
    projectsKind.aggregate_method = "get_projects_kind_aggregate"

    projectsCity.specs = "get_projects_city_specs"
    projectsCity.aggregate_method = "get_projects_city_aggregate"

    class Meta:
        model = News
        fields = ("project", "type")

    @staticmethod
    def type_filter(queryset, name, value):
        q = Q()
        for v in value:
            if v == "video":
                q |= Q(
                    Q(type=NewsType.VIDEO)
                    | (
                        Q(type=NewsType.PROGRESS)
                        & Q(newsslide__isnull=False)
                        & ~Q(newsslide__video="")
                    )
                )
            elif v == "progress":
                q |= Q(
                    Q(type=NewsType.PROGRESS) & Q(newsslide__isnull=False) & ~Q(newsslide__image="")
                )
            else:
                q |= Q(type=v)
        return queryset.filter(q)

    @staticmethod
    def filter_projects_kind(queryset, name, value):
        if value:
            if value == "commercial":
                return queryset.filter(projects__is_commercial=True)
            elif value == "residential":
                return queryset.filter(projects__is_residential=True)
        return queryset

    @staticmethod
    def get_projects_kind_specs(queryset):
        res = (
            queryset.annotate(
                label=Case(
                    When(projects__is_commercial=True, then=Value("Коммерческие")),
                    When(projects__is_residential=True, then=Value("Жилые")),
                    output_field=CharField(),
                ),
                value=Case(
                    When(projects__is_commercial=True, then=Value("commercial")),
                    When(projects__is_residential=True, then=Value("residential")),
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
    def get_projects_city_specs(queryset):
        res = (
            queryset.annotate(label=F("projects__city__name"), value=F("projects__city__id"))
            .filter(label__isnull=False, value__isnull=False)
            .values("label", "value")
            .order_by("label", "value")
            .distinct("label", "value")
        )
        specs = [
            {"label": i["label"], "value": to_global_id(CityType.__name__, i["value"])} for i in res
        ]
        return specs

    @staticmethod
    def get_type_specs(queryset):
        qs = (
            queryset.all()
            .filter(type="progress")
            .aggregate(
                count_images=Count("id", Q(newsslide__isnull=False) & ~Q(newsslide__image="")),
                count_videos=Count("id", Q(newsslide__isnull=False) & ~Q(newsslide__video="")),
            )
        )
        res = list(queryset.order_by("type").values_list("type", flat=True).distinct())
        if qs["count_images"] == 0 and NewsType.PROGRESS in res:
            res.remove(NewsType.PROGRESS)
        if qs["count_videos"] > 0 and NewsType.VIDEO not in res:
            res.append(NewsType.VIDEO)
        specs = [{"label": dict(NewsType.choices)[i], "value": i} for i in res]
        return specs

    @staticmethod
    def get_projects_kind_aggregate(queryset):
        aggregate = (
            queryset.annotate(
                value=Case(
                    When(projects__is_commercial=True, then=Value("commercial")),
                    When(projects__is_residential=True, then=Value("residential")),
                    output_field=CharField(),
                )
            )
            .filter(value__isnull=False)
            .order_by("value")
            .distinct("value")
            .values_list("value", flat=True)
        )
        return aggregate

    @staticmethod
    def get_projects_city_aggregate(queryset):
        res = (
            queryset.annotate(value=F("projects__city__id"))
            .filter(value__isnull=False)
            .order_by("value")
            .distinct("value")
            .values_list("value", flat=True)
        )
        aggregate = [to_global_id(CityType.__name__, i) for i in res]
        return aggregate

    @staticmethod
    def type_aggregate(queryset):
        qs = (
            queryset.all()
            .filter(type="progress")
            .aggregate(
                count_images=Count("id", Q(newsslide__isnull=False) & ~Q(newsslide__image="")),
                count_videos=Count("id", Q(newsslide__isnull=False) & ~Q(newsslide__video="")),
            )
        )
        aggregate = list(queryset.order_by("type").values_list("type", flat=True).distinct())
        if qs["count_images"] == 0 and NewsType.PROGRESS in aggregate:
            aggregate.remove(NewsType.PROGRESS)
        if qs["count_videos"] > 0 and NewsType.VIDEO not in aggregate:
            aggregate.append(NewsType.VIDEO.value)
        return aggregate
