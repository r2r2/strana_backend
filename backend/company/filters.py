from graphql_relay import from_global_id
from django.db.models import F, Q
from django_filters import CharFilter, BooleanFilter
from graphene_django.filter import GlobalIDFilter
from graphene_django.filter.filterset import GrapheneFilterSetMixin, GlobalIDMultipleChoiceFilter
from graphql_relay import to_global_id
from .models import Document, Vacancy, OffersDocument, DocumentCategory
from common.filters import FacetFilterSet


class DocumentFilter(FacetFilterSet):
    """
    Фильтр документов
    """

    city = GlobalIDFilter(method="filter_city", label="Фильтр по городу")
    project = GlobalIDFilter(field_name="project__id", label="Фильтр по проекту")
    category = GlobalIDFilter(field_name="category__id", label="Фильтр по категории")
    building = GlobalIDFilter(field_name="building__id", label="Фильтр по корпусу")
    is_investors = BooleanFilter(
        field_name="is_investors", label="Показывать на странице инвесторов"
    )

    project.specs = "get_project_specs"
    city.specs = "get_city_specs"
    building.specs = "get_building_specs"
    category.specs = "get_category_specs"

    project.aggregate_method = "get_project_aggregate"
    city.aggregate_method = "get_city_aggregate"
    building.aggregate_method = "get_building_aggregate"
    category.aggregate_method = "get_category_aggregate"

    @staticmethod
    def filter_city(queryset, name, value):
        _, city = from_global_id(value)
        return queryset.filter(Q(project__city__id=city) | Q(project__isnull=True))

    @staticmethod
    def get_project_specs(queryset):
        from projects.schema import GlobalProjectType

        qs = (
            queryset.filter(project__isnull=False)
            .annotate(label=F("project__name"), value=F("project__id"))
            .order_by("label", "value")
            .distinct("label", "value")
            .values("label", "value")
        )
        specs = [
            {"label": i["label"], "value": to_global_id(GlobalProjectType.__name__, i["value"])}
            for i in qs
        ]
        return specs

    @staticmethod
    def get_city_specs(queryset):
        from cities.schema import CityType

        qs = (
            queryset.filter(category__isnull=False)
            .annotate(label=F("project__city__name"), value=F("project__city__id"))
            .order_by("label", "value")
            .distinct("label", "value")
            .values("label", "value")
        )
        specs = [
            {"label": i["label"], "value": to_global_id(CityType.__name__, i["value"])} for i in qs
        ]
        return specs

    @staticmethod
    def get_building_specs(queryset):
        from buildings.schema import BuildingType

        qs = (
            queryset.filter(building__isnull=False)
            .annotate(label=F("building__name_display"), value=F("building__id"))
            .order_by("label", "value")
            .distinct("label", "value")
            .values("label", "value")
        )
        specs = [
            {"label": i["label"], "value": to_global_id(BuildingType.__name__, i["value"])}
            for i in qs
        ]
        return specs

    @staticmethod
    def get_category_specs(queryset):
        from .schemas import DocumentCategoryType

        qs = (
            DocumentCategory.objects.filter(id__isnull=False)
            .annotate(label=F("title"), value=F("id"))
            .order_by("label", "value")
            .distinct("label", "value")
            .values("label", "value")
        )
        specs = [
            {"label": i["label"], "value": to_global_id(DocumentCategoryType.__name__, i["value"])}
            for i in qs
        ]
        return specs

    @staticmethod
    def get_project_aggregate(queryset):
        from projects.schema import GlobalProjectType

        qs = (
            queryset.filter(project__isnull=False)
            .order_by("project__id")
            .distinct("project__id")
            .values_list("project__id", flat=True)
        )
        aggregate = [to_global_id(GlobalProjectType.__name__, i) for i in qs]
        return aggregate

    @staticmethod
    def get_city_aggregate(queryset):
        from cities.schema import CityType

        qs = (
            queryset.filter(project__city__isnull=False)
            .order_by("project__city__id")
            .distinct("project__city__id")
            .values_list("project__city__id", flat=True)
        )
        aggregate = [to_global_id(CityType.__name__, i) for i in qs]
        return aggregate

    @staticmethod
    def get_building_aggregate(queryset):
        from buildings.schema import BuildingType

        qs = (
            queryset.filter(building__id__isnull=False)
            .order_by("building__id")
            .distinct("building__id")
            .values_list("building__id", flat=True)
        )
        aggregate = [to_global_id(BuildingType.__name__, i) for i in qs]
        return aggregate

    @staticmethod
    def get_category_aggregate(queryset):
        from .schemas import DocumentCategoryType

        qs = (
            DocumentCategory.objects.filter(id__isnull=False)
            .order_by("id")
            .distinct("id")
            .values_list("id", flat=True)
        )
        aggregate = [to_global_id(DocumentCategoryType.__name__, i) for i in qs]
        return aggregate

    class Meta:
        model = Document
        fields = ("city", "project", "category", "building")


class VacancyFilterSet(GrapheneFilterSetMixin, FacetFilterSet):
    """
    Фильтр вакансий
    """

    city = GlobalIDFilter(field_name="city", label="Фильтр по городу")
    category = GlobalIDFilter(field_name="category", label="Фильтр по категории")
    text = CharFilter(field_name="job_title", lookup_expr="icontains", label="Фильтр по названию")

    class Meta:
        model = Vacancy
        fields = ("city", "category", "text")


class OffersDocumentFilter(FacetFilterSet):
    """
    Фильтр документов оферты и политики обработки данных
    """

    cities = GlobalIDMultipleChoiceFilter(field_name="cities", label="ID города")

    class Meta:
        model = OffersDocument
        fields = ("cities",)
