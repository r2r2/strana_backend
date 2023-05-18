from copy import copy

from django.db.models import Case, CharField, F
from django.db.models import Prefetch as P
from django.db.models import Q, Value, When

from graphene_django.filter.filterset import (GlobalIDFilter,
                                              GlobalIDMultipleChoiceFilter,
                                              GrapheneFilterSetMixin)
from graphql_relay import to_global_id
from buildings.models import Building
from buildings.schema import BuildingType
from cities.models import City
from django_filters import (
    BaseInFilter, BooleanFilter, CharFilter,
    ChoiceFilter, Filter, MultipleChoiceFilter, NumberFilter, OrderingFilter,
    RangeFilter
)
from cities.schema import CityType
from cities.serializers import (CityCategorySerializer,
                                ProjectCategorySerializer)
from common.filters import (FacetFilterSet, FloatFilter, IntegerFilter,
                            ListInFilter, NumberInFilter)
from common.utils import to_snake_case
from graphene.utils.str_converters import to_camel_case
from mortgage.constants import MortgageType
from projects.models import Project
from projects.schema import ProjectType

from .constants import FeatureType, PropertyStatus
from .constants import PropertyType as PropertyTypeChoices
from .constants import SimilarPropertiesTab
from .models import (Feature, Furnish, FurnishFurniture, FurnishKitchen,
                     Layout, ListingAction, Property)




class BasePropertyFilterSet(GrapheneFilterSetMixin, FacetFilterSet):
    """
    Базовый фильтр объектов собственности
    """

    id = GlobalIDMultipleChoiceFilter(field_name="id", label="Фильтр по ID")
    project = GlobalIDMultipleChoiceFilter(field_name="project__slug", label="Фильтр по проекту")
    building = GlobalIDMultipleChoiceFilter(field_name="building", label="Фильтр по корпусу")
    price = RangeFilter(field_name="price", label="Фильтр по цене")
    area = RangeFilter(field_name="area", label="Фильтр по площади")
    completion_date = CharFilter(method="completion_date_filter", label="Фильтр по завершению")
    is_favorite = BooleanFilter(field_name="is_favorite", label="Фильтр по избранным")
    action = BooleanFilter(field_name="has_discount", label="Фильтр по акции")
    installment = BooleanFilter(field_name="installment", label="Фильтр по рассрочке")
    orderBy = OrderingFilter(
        fields=("price", "area", "id", ("floor__number", "floor"), ("views_count", "popular")),
        label="Упорядочивание",
    )
    article = CharFilter(field_name="article", label="Фильтр по артикулу")
    article_list = MultipleChoiceFilter(
        choices=[(item["article"], item["article"]) for item in Property.objects.all().values("article")],
        lookup_expr="in", label="Фильтр по списку артикулов", field_name="article",
        method="filter_articles"
    )
    features = ListInFilter(method="filter_features", label="Фильтр по особенностям")
    special_offers = ListInFilter(field_name="specialoffer__id", label="Фильтр по акциям")

    project.specs = "get_project_specs"
    project.aggregate_method = "aggregate_projects"

    building.specs = "get_building_specs"

    completion_date.specs = "get_completion_date_specs"
    completion_date.aggregate_method = "aggregate_completion_date"

    features.specs = "get_features_specs"
    features.aggregate_method = "aggregate_features"

    special_offers.specs = "get_special_offers_specs"
    special_offers.aggregate_method = "aggregate_special_offers"

    class Meta:
        model = Property
        fields = ()

    def filter_queryset(self, queryset):
        if "features" in self.data:
            queryset = self.filter_features(queryset, "features", self.data["features"])
        return super().filter_queryset(queryset)

    @staticmethod
    def filter_articles(queryset, name, value):
        if not value or not isinstance(value, list):
            return queryset
        return queryset.filter(article__in=value)

    @staticmethod
    def completion_date_filter(queryset, name, value):
        try:
            year, quarter = value.split("-")
            year, quarter = int(year), int(quarter)
        except ValueError:
            return queryset
        return queryset.filter(building__ready_quarter=quarter, building__built_year=year)

    @staticmethod
    def get_project_specs(queryset):
        res = (
            queryset.annotate(label=F("project__name"), value=F("project__slug"))
            .values("label", "value")
            .order_by("project__order", "project__id")
            .distinct("project__order", "project__id")
        )
        specs = [
            {"label": i["label"], "value": to_global_id(ProjectType.__name__, i["value"])}
            for i in res
        ]
        return specs

    @staticmethod
    def get_building_specs(queryset):
        res = (
            queryset.annotate(label=F("building__name_display"), value=F("building_id"))
            .values("label", "value")
            .order_by("building_id")
            .distinct("building_id")
        )
        specs = [
            {"label": i["label"], "value": to_global_id(BuildingType.__name__, i["value"])}
            for i in res
        ]
        return specs

    @staticmethod
    def aggregate_projects(queryset):
        res = (
            queryset.order_by("project__order", "project__id")
            .distinct("project__order", "project__id")
            .values_list("project__slug", flat=True)
        )
        aggregate = [to_global_id(ProjectType.__name__, i) for i in res]
        return aggregate

    @staticmethod
    def get_completion_date_specs(queryset):
        res = (
            queryset.annotate(quarter=F("building__ready_quarter"), year=F("building__built_year"))
            .filter(Q(quarter__isnull=False) | Q(year__isnull=False))
            .values("quarter", "year")
            .order_by("year", "quarter")
            .distinct("year", "quarter")
        )
        specs = [
            {"label": f"{i['quarter']} кв. {i['year']}", "value": f"{i['year']}-{i['quarter']}"}
            for i in res
        ]
        return specs

    @staticmethod
    def aggregate_completion_date(queryset):
        res = (
            queryset.annotate(quarter=F("building__ready_quarter"), year=F("building__built_year"))
            .filter(Q(quarter__isnull=False) | Q(year__isnull=False))
            .values("quarter", "year")
            .order_by("year", "quarter")
            .distinct("year", "quarter")
        )
        aggregate = [f"{i['year']}-{i['quarter']}" for i in res]
        return aggregate

    @staticmethod
    def filter_features(queryset, name, value):
        filter_ = {
            to_snake_case(val): True for val in value if to_snake_case(val) in FeatureType.values
        }
        return queryset.filter(**filter_)

    def get_features_specs(self, queryset):
        features = (
            Feature.objects.for_filter(self.PROPERTY_TYPE, self.request)
            .annotate(value=F("kind"), label=F("name"))
            .values(
                "label",
                "value",
                "description",
                "icon",
                "icon_hypo",
                "icon_show",
                "main_filter_show",
                "is_button",
            )
        )

        specs = [
            {
                "label": f["label"],
                "value": to_camel_case(f["value"]),
                "description": f["description"],
                "icon": f["icon"],
                "icon_hypo": f["icon_hypo"],
                "icon_show": f["icon_show"],
                "main_filter_show": f["main_filter_show"],
                "is_button": f["is_button"],
            }
            for f in features
        ]
        return specs

    def aggregate_features(self, queryset):

        kinds = Feature.objects.for_filter(self.PROPERTY_TYPE, self.request).values_list(
            "kind", flat=True
        )

        features = []
        for kind in kinds:
            filter_ = {kind: True}
            camel_kind = to_camel_case(kind)
            if queryset.filter(**filter_).exists() and camel_kind not in features:
                features.append(camel_kind)
        return features

    @staticmethod
    def get_special_offers_specs(queryset):
        specs = (
            queryset.filter(specialoffer__is_display=True)
            .annotate(label=F("specialoffer__name"), value=F("specialoffer__id"))
            .values("label", "value")
            .order_by("value")
            .distinct("value")
        )
        return specs

    @staticmethod
    def aggregate_special_offers(queryset):
        res = (
            queryset.filter(specialoffer__is_display=True,
                            specialoffer__is_active=True)
            .annotate(value=F("specialoffer__id"))
            .values_list("value", flat=True)
            .order_by("value")
            .distinct("value")
        )
        return res


class FlatFilterSet(BasePropertyFilterSet):
    """
    Фильтр квартир
    """

    PROPERTY_TYPE = PropertyTypeChoices.FLAT

    rooms = ListInFilter(field_name="rooms", method="filter_rooms", label="Фильтр по комнатам")
    floor = RangeFilter(field_name="floor__number", label="Фильтр по этажу")
    balconiesCount = BaseInFilter(field_name="balconies_count", label="Фильтр по кол-ву балконов")
    loggiasCount = NumberInFilter(field_name="loggias_count", label="Фильтр по кол-ву лоджей")
    storesCount = NumberInFilter(field_name="stores_count", label="Фильтр по кол-ву кладовых")
    wardrobesCount = NumberInFilter(
        field_name="wardrobes_count", label="Фильтр по кол-ву гардеробных"
    )
    landingBlock = NumberFilter(field_name="landingblock", label="Фильтр по блоку лендинга")
    landingBlock.skip = True
    deposit = FloatFilter(
        field_name="project__offer__deposit",
        label="Для фильтра по платежу(поле депозита)",
        lookup_expr="icontains",
    )
    min_mortgage = RangeFilter(field_name="hypo_min_mortgage", label="Фильтр по платежу")
    mortgage_type = ChoiceFilter(
        field_name="project__offer__type", choices=MortgageType.choices, label="Фильтр по типу"
    )
    mortgage_type.skip = True

    rooms.specs = "get_rooms_specs"
    rooms.aggregate_method = "rooms_aggregate"

    class Meta:
        model = Property
        fields = ("building", "facing", *BasePropertyFilterSet.Meta.fields)

    @staticmethod
    def filter_rooms(queryset, name, value):
        return queryset.annotate(
            rooms_value=Case(
                When(Q(rooms__gte=4), then=Value("4")), default=F("rooms"), output_field=CharField()
            )
        ).filter(rooms_value__isnull=False, rooms_value__in=value)

    @staticmethod
    def get_rooms_specs(queryset):
        specs = [
            {"label": "Студия", "value": "0"},
            {"label": "1", "value": "1"},
            {"label": "2", "value": "2"},
            {"label": "3", "value": "3"},
            {"label": "4+", "value": "4"},
        ]
        return specs

    @staticmethod
    def rooms_aggregate(queryset):
        aggregate = (
            queryset.annotate(
                rooms_value=Case(
                    When(Q(rooms__gte=4), then=Value("4")),
                    default=F("rooms"),
                    output_field=CharField(),
                )
            )
            .filter(rooms_value__isnull=False)
            .order_by("rooms_value")
            .distinct("rooms_value")
            .values_list("rooms_value", flat=True)
        )
        return aggregate

    def facets(self):
        facets = super().facets()
        facets.update(dict(
            with_commercial=self.qs.filter(type=PropertyTypeChoices.COMMERCIAL).exists(),
            with_flat=self.qs.filter(type=PropertyTypeChoices.FLAT).exists(),
            with_commercial_apartment=self.qs.filter(type=PropertyTypeChoices.COMMERCIAL_APARTMENT).exists()
        ))
        return facets


class GlobalFlatFilterSet(FlatFilterSet):
    """
    Фильтр глобальных квартир
    """

    city = GlobalIDFilter(field_name="project__city__id", label="Фильтр по городу")


    city.specs = "get_city_specs"
    city.aggregate_method = "aggregate_cities"

    buildingCategory = Filter(label="Группировка корпусов по проекту")
    buildingCategory.specs = "get_building_category_specs"

    projectCategory = Filter(label="Группировка проектов по городу")
    projectCategory.specs = "get_project_category_specs"

    @staticmethod
    def get_building_category_specs(queryset):
        serializer = ProjectCategorySerializer(
            Project.objects.annotate_flats_count()
            .filter(flats_count__gt=0, active=True)
            .prefetch_related(
                P("building_set", Building.objects.annotate_flats_count().filter(flats_count__gt=0))
            ),
            many=True,
        )
        return serializer.data

    @staticmethod
    def get_project_category_specs(queryset):
        serializer = CityCategorySerializer(
            City.objects.annotate_has_active_projects()
            .filter(has_active_projects=True)
            .prefetch_related("project_set"),
            many=True,
        )
        return serializer.data

    @staticmethod
    def get_city_specs(queryset):
        res = (
            queryset.annotate(label=F("project__city__name"), value=F("project__city__id"))
            .values("label", "value")
            .order_by("project__city__order", "project__city__id")
            .distinct("project__city__order", "project__city__id")
        )
        specs = [
            {"label": i["label"], "value": to_global_id(CityType.__name__, i["value"])} for i in res
        ]
        return specs

    @staticmethod
    def aggregate_cities(queryset):
        res = (
            queryset.order_by("project__city__order", "project__city__id")
            .distinct("project__city__order", "project__city__id")
            .values_list("project__city__id", flat=True)
        )
        aggregate = [to_global_id(CityType.__name__, i) for i in res]
        return aggregate

    class Meta:
        model = Property
        fields = ("city", *FlatFilterSet.Meta.fields)


class ParkingSpaceFilterSet(BasePropertyFilterSet):
    """
    Фильтр парковочных мест
    """

    PROPERTY_TYPE = PropertyTypeChoices.PARKING


class PantrySpaceFilterSet(BasePropertyFilterSet):
    """
    Фильтр кладовых мест мест
    """

    PROPERTY_TYPE = PropertyTypeChoices.PANTRY


class ParkingPantrySpaceFilterSet(BasePropertyFilterSet):
    """
    Фильтр кладовых мест мест
    """
    PROPERTY_TYPE = PropertyTypeChoices.PARKING


class GlobalParkingSpaceFilterSet(ParkingSpaceFilterSet):
    """
    Фильтр глобальных парковочных мест
    """

    city = GlobalIDFilter(field_name="project__city__id", label="Фильтр по городу")
    project = GlobalIDFilter(field_name="project__slug", label="Фильтр по проекту")
    building = GlobalIDFilter(field_name="building", label="Фильтр по корпусу")

    floor = GlobalIDFilter(field_name="floor", label="Фильтр по этажу")
    floor.skip = True

    city.specs = "get_city_specs"
    city.aggregate_method = "aggregate_cities"

    project.specs = "get_project_specs"
    project.aggregate_method = "aggregate_projects"

    building.specs = "get_building_specs"

    class Meta:
        model = Property
        fields = ("city", *FlatFilterSet.Meta.fields)

    @staticmethod
    def get_city_specs(queryset):
        res = (
            queryset.annotate(label=F("project__city__name"), value=F("project__city__id"))
            .values("label", "value")
            .order_by("project__city__order", "project__city__id")
            .distinct("project__city__order", "project__city__id")
        )
        specs = [
            {"label": i["label"], "value": to_global_id(CityType.__name__, i["value"])} for i in res
        ]
        return specs

    @staticmethod
    def aggregate_cities(queryset):
        res = (
            queryset.order_by("project__city__order", "project__city__id")
            .distinct("project__city__order", "project__city__id")
            .values_list("project__city__id", flat=True)
        )
        aggregate = [to_global_id(CityType.__name__, i) for i in res]
        return aggregate

    @staticmethod
    def get_building_specs(queryset):
        res = (
            queryset.annotate(label=F("building__name"), value=F("building_id"))
            .values("label", "value")
            .order_by("building_id")
            .distinct("building_id")
        )
        specs = [
            {"label": i["label"], "value": to_global_id(BuildingType.__name__, i["value"])}
            for i in res
        ]
        return specs


class GlobalPantrySpaceFilterSet(PantrySpaceFilterSet):
    """
    Фильтр глобальных парковочных мест
    """

    city = GlobalIDFilter(field_name="project__city__id", label="Фильтр по городу")
    project = GlobalIDFilter(field_name="project__slug", label="Фильтр по проекту")
    building = GlobalIDFilter(field_name="building", label="Фильтр по корпусу")

    floor = GlobalIDFilter(field_name="floor", label="Фильтр по этажу")
    floor.skip = True

    city.specs = "get_city_specs"
    city.aggregate_method = "aggregate_cities"

    project.specs = "get_project_specs"
    project.aggregate_method = "aggregate_projects"

    building.specs = "get_building_specs"

    class Meta:
        model = Property
        fields = ("city", *FlatFilterSet.Meta.fields)

    @staticmethod
    def get_city_specs(queryset):
        res = (
            queryset.annotate(label=F("project__city__name"), value=F("project__city__id"))
                .values("label", "value")
                .order_by("project__city__order", "project__city__id")
                .distinct("project__city__order", "project__city__id")
        )
        specs = [
            {"label": i["label"], "value": to_global_id(CityType.__name__, i["value"])} for i in res
        ]
        return specs

    @staticmethod
    def aggregate_cities(queryset):
        res = (
            queryset.order_by("project__city__order", "project__city__id")
                .distinct("project__city__order", "project__city__id")
                .values_list("project__city__id", flat=True)
        )
        aggregate = [to_global_id(CityType.__name__, i) for i in res]
        return aggregate

    @staticmethod
    def get_building_specs(queryset):
        res = (
            queryset.annotate(label=F("building__name"), value=F("building_id"))
                .values("label", "value")
                .order_by("building_id")
                .distinct("building_id")
        )
        specs = [
            {"label": i["label"], "value": to_global_id(BuildingType.__name__, i["value"])}
            for i in res
        ]
        return specs


class GlobalParkingPantrySpaceFilterSet(ParkingPantrySpaceFilterSet):
    """
    Фильтр глобальных парковочных мест и кладовых
    """
    types = ListInFilter(method="filter_types", label="Фильтр по типу")
    city = GlobalIDFilter(field_name="project__city__id", label="Фильтр по городу")
    project = GlobalIDFilter(field_name="project__slug", label="Фильтр по проекту")
    building = GlobalIDFilter(field_name="building", label="Фильтр по корпусу")

    floor = GlobalIDFilter(field_name="floor", label="Фильтр по этажу")
    floor.skip = True

    city.specs = "get_city_specs"
    city.aggregate_method = "aggregate_cities"

    project.specs = "get_project_specs"
    project.aggregate_method = "aggregate_projects"

    building.specs = "get_building_specs"

    class Meta:
        model = Property
        fields = ("city", *FlatFilterSet.Meta.fields)

    @staticmethod
    def filter_types(queryset, name, value):
        return queryset.filter(type__in=value)

    @staticmethod
    def get_city_specs(queryset):
        res = (
            queryset.annotate(label=F("project__city__name"), value=F("project__city__id"))
                .values("label", "value")
                .order_by("project__city__order", "project__city__id")
                .distinct("project__city__order", "project__city__id")
        )
        specs = [
            {"label": i["label"], "value": to_global_id(CityType.__name__, i["value"])} for i in res
        ]
        return specs

    @staticmethod
    def aggregate_cities(queryset):
        res = (
            queryset.order_by("project__city__order", "project__city__id")
                .distinct("project__city__order", "project__city__id")
                .values_list("project__city__id", flat=True)
        )
        aggregate = [to_global_id(CityType.__name__, i) for i in res]
        return aggregate

    @staticmethod
    def get_building_specs(queryset):
        res = (
            queryset.annotate(label=F("building__name"), value=F("building_id"))
                .values("label", "value")
                .order_by("building_id")
                .distinct("building_id")
        )
        specs = [
            {"label": i["label"], "value": to_global_id(BuildingType.__name__, i["value"])}
            for i in res
        ]
        return specs

class CommercialSpaceFilterSet(BasePropertyFilterSet):
    """
    Фильтр коммерческих помещений
    """

    PROPERTY_TYPE = PropertyTypeChoices.COMMERCIAL

    hasTenant = BooleanFilter(field_name="has_tenant", label="Фильтр по арендатору")
    completed = BooleanFilter(field_name="completed", label="Фильтр по завершенности")


class GlobalCommercialSpaceFilterSet(CommercialSpaceFilterSet):
    """
    Фильтр глобальных коммерческих помещений
    """

    city = GlobalIDFilter(field_name="project__city__id", label="Фильтр по городу")
    building = GlobalIDMultipleChoiceFilter(field_name="building", label="Фильтр по корпусу")
    has_auction = BooleanFilter(field_name="has_auction", label="Фильтр по наличию аукциона")
    purposes = ListInFilter(field_name="purposes", label="Фильтр по назначениям помещения")
    tab = ChoiceFilter(
        method="filter_tab", choices=SimilarPropertiesTab.choices, label="Фильтр по табу"
    )

    tab.specs = "get_tab_specs"
    tab.aggregate_method = "aggregate_tabs"

    city.specs = "get_city_specs"
    city.aggregate_method = "aggregate_cities"

    purposes.specs = "get_purposes_specs"
    purposes.aggregate_method = "purposes_aggregate"

    class Meta:
        model = Property
        fields = ("city", *FlatFilterSet.Meta.fields)

    def filter_tab(self, qs, name, value):
        if value == SimilarPropertiesTab.WITH_FURNISH:
            qs = qs.filter(furnish_set__isnull=False)
        return qs

    @staticmethod
    def aggregate_tabs(queryset):
        res = []
        if queryset.filter(furnish_set__isnull=False).exists():
            res.append(SimilarPropertiesTab.WITH_FURNISH)
        return res

    @staticmethod
    def get_city_specs(queryset):
        res = (
            queryset.annotate(label=F("project__city__name"), value=F("project__city__id"))
            .values("label", "value")
            .order_by("project__city__order", "project__city__id")
            .distinct("project__city__order", "project__city__id")
        )
        specs = [
            {"label": i["label"], "value": to_global_id(CityType.__name__, i["value"])} for i in res
        ]
        return specs

    @staticmethod
    def aggregate_cities(queryset):
        res = (
            queryset.order_by("project__city__order", "project__city__id")
            .distinct("project__city__order", "project__city__id")
            .values_list("project__city__id", flat=True)
        )
        aggregate = [to_global_id(CityType.__name__, i) for i in res]
        return aggregate

    @staticmethod
    def get_purposes_specs(queryset):
        res = (
            queryset.annotate(label=F("purposes__name"), value=F("purposes__id"))
            .values("label", "value")
            .order_by("purposes__order")
            .distinct("purposes__order")
        )
        specs = [{"label": i["label"], "value": i["value"]} for i in res]
        return specs

    @staticmethod
    def purposes_aggregate(queryset):
        aggregate = (
            queryset.filter(purposes__isnull=False)
            .values_list("purposes__id", flat=True)
            .order_by("purposes__order")
            .distinct("purposes__order")
        )
        return aggregate

    @classmethod
    def get_tab_specs(cls, queryset):
        qs_for_furnish = copy(queryset).filter(furnish_set__isnull=False)
        specs = []
        if qs_for_furnish:
            specs.append({"value": SimilarPropertiesTab.WITH_FURNISH, "label": "С отделкой"})
        return specs


class UniquePlanFilterSet(GrapheneFilterSetMixin, FacetFilterSet):
    """
    Фильтр уникальных планировок
    """

    city = GlobalIDFilter(field_name="project__city__id")
    project = GlobalIDFilter(field_name="project__slug")
    rooms = ListInFilter(field_name="rooms", method="filter_rooms")

    rooms.specs = "get_rooms_specs"
    rooms.aggregate_method = "rooms_aggregate"

    project.specs = "get_project_specs"
    project.aggregate_method = "aggregate_projects"

    city.specs = "get_city_specs"
    city.aggregate_method = "aggregate_cities"

    @staticmethod
    def filter_rooms(queryset, name, value):
        return queryset.annotate(
            rooms_value=Case(
                When(Q(rooms__gte=4), then=Value("4")), default=F("rooms"), output_field=CharField()
            )
        ).filter(rooms_value__isnull=False, rooms_value__in=value)

    @staticmethod
    def get_project_specs(queryset):
        res = (
            queryset.annotate(label=F("project__name"), value=F("project__slug"))
            .values("label", "value")
            .order_by("project__order", "project__id")
            .distinct("project__order", "project__id")
        )
        specs = [
            {"label": i["label"], "value": to_global_id(ProjectType.__name__, i["value"])}
            for i in res
        ]
        return specs

    @staticmethod
    def aggregate_projects(queryset):
        res = (
            queryset.order_by("project__order", "project__id")
            .distinct("project__order", "project__id")
            .values_list("project__slug", flat=True)
        )
        aggregate = [to_global_id(ProjectType.__name__, i) for i in res]
        return aggregate

    @staticmethod
    def get_city_specs(queryset):
        res = (
            queryset.annotate(label=F("project__city__name"), value=F("project__city__id"))
            .values("label", "value")
            .order_by("project__city__order", "project__city__id")
            .distinct("project__city__order", "project__city__id")
        )
        specs = [
            {"label": i["label"], "value": to_global_id(CityType.__name__, i["value"])} for i in res
        ]
        return specs

    @staticmethod
    def aggregate_cities(queryset):
        res = (
            queryset.order_by("project__city__order", "project__city__id")
            .distinct("project__city__order", "project__city__id")
            .values_list("project__city__id", flat=True)
        )
        aggregate = [to_global_id(CityType.__name__, i) for i in res]
        return aggregate

    @staticmethod
    def get_rooms_specs(queryset):
        specs = [
            {"label": "Студия", "value": "0"},
            {"label": "1-ком.", "value": "1"},
            {"label": "2-ком.", "value": "2"},
            {"label": "3-ком.", "value": "3"},
            {"label": "4-ком. и более", "value": "4"},
        ]
        return specs

    @staticmethod
    def rooms_aggregate(queryset):
        aggregate = (
            queryset.annotate(
                rooms_value=Case(
                    When(Q(rooms__gte=4), then=Value("4")),
                    default=F("rooms"),
                    output_field=CharField(),
                )
            )
            .filter(rooms_value__isnull=False)
            .order_by("rooms_value")
            .distinct("rooms_value")
            .values_list("rooms_value", flat=True)
        )
        return aggregate

    class Meta:
        model = Property
        fields = ("city", "rooms", *BasePropertyFilterSet.Meta.fields)


class SimilarPropertyFilterSet(GrapheneFilterSetMixin, FacetFilterSet):
    """
    Фильтр похожих объектов собственности
    """

    tab = ChoiceFilter(
        method="filter_tab", choices=SimilarPropertiesTab.choices, label="Фильтр по табу"
    )

    tab.specs = "get_tab_specs"

    class Meta:
        model = Property
        fields = (*BasePropertyFilterSet.Meta.fields,)

    def filter_tab(self, qs, name, value):
        if value == SimilarPropertiesTab.LESS_PRICE:
            qs = qs.filter(price__lte=F("base_price"))
        elif value == SimilarPropertiesTab.LARGER_AREA:
            qs = qs.filter(area__gte=F("base_area"))
        elif value == SimilarPropertiesTab.WITH_FURNISH:
            qs = qs.filter(furnish_set__isnull=False)
        return qs

    @classmethod
    def get_tab_specs(cls, queryset):
        qs_for_less = copy(queryset).filter(price__lte=F("base_price"))
        qs_for_larger = copy(queryset).filter(area__gte=F("base_area"))
        qs_for_furnish = copy(queryset).filter(furnish_set__isnull=False)
        specs = []
        if qs_for_less:
            specs.append({"value": SimilarPropertiesTab.LESS_PRICE, "label": "Дешевле"})
        if qs_for_larger:
            specs.append({"value": SimilarPropertiesTab.LARGER_AREA, "label": "Больше площадь"})
        if qs_for_furnish:
            specs.append({"value": SimilarPropertiesTab.WITH_FURNISH, "label": "С отделкой"})
        return specs


class LayoutFilterSet(FacetFilterSet):
    order = OrderingFilter(fields=("price", "area", "flat_sold"), label="Сортировка")
    order_most_expensive = BooleanFilter(method="order_most_expensive_ordering")
    order_popular = BooleanFilter(method="order_popular_ordering", label="Сортировка по популярным")
    order_popular.pop = True
    order_random = BooleanFilter(method="order_random_ordering", label="Случайная сортировка")

    class Meta:
        model = Layout
        fields = ("order_random", "order_most_expensive", "order_popular", "order")

    @staticmethod
    def order_most_expensive_ordering(queryset, name, value):
        if value:
            qs = queryset.annotate_most_expensive()
            return qs.order_by("most_expensive", "price")
        return queryset

    @staticmethod
    def order_popular_ordering(queryset, name, value):
        if value:
            return queryset.order_by("-hypo_popular")
        return queryset

    @staticmethod
    def order_random_ordering(queryset, name, value):
        if value:
            return queryset.order_by("?")
        return queryset


class FurnishFilterSet(FacetFilterSet):
    project = GlobalIDFilter(field_name="project__slug", label="Фильтр по проекту")

    class Meta:
        model = Furnish
        fields = ()


class FurnishKitchenFilterSet(FacetFilterSet):
    project = GlobalIDFilter(field_name="project__slug", label="Фильтр по проекту")

    class Meta:
        model = FurnishKitchen
        fields = ()


class FurnishFurnitureFilterSet(FacetFilterSet):
    project = GlobalIDFilter(field_name="project__slug", label="Фильтр по проекту")

    class Meta:
        model = FurnishFurniture
        fields = ()


class ListingActionFilterSet(FacetFilterSet):
    city = GlobalIDFilter(field_name="city", label="Фильтр по городу")

    class Meta:
        model = ListingAction
        fields = ()
