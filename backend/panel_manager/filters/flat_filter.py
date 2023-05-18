from django.db.models import Case, CharField, F, Q, Value, When
from django.db.models.functions import Concat
from django_filters import BaseInFilter
from django_filters.rest_framework import Filter, OrderingFilter, RangeFilter, BooleanFilter
from graphene.utils.str_converters import to_camel_case

from common.filters import FacetFilterSet, NumberInFilter, CharInFilter
from common.utils import to_snake_case
from properties.constants import PropertyType, FeatureType
from properties.models import Property, Feature


class FlatFilter(FacetFilterSet):
    PROPERTY_TYPE = PropertyType.FLAT

    ids = NumberInFilter(label="Фильтр по id", field_name="id")
    ids.skip = True
    project = BaseInFilter(label="Фильтр по проектам")
    building = NumberInFilter(label="Фильтр по корпусам")
    section = NumberInFilter(label="Фильтр по секциям", field_name="section_id")
    section.specs = "section_specs"
    # section.skip = True
    section_group = NumberInFilter(label="Фильтр по группас секций", field_name="section__group")
    section_group.specs = "section_group_specs"
    # section_group.skip = True
    rooms = NumberInFilter(method="rooms_filter", label="Фильтр по комнатности")
    rooms.specs = "get_rooms_specs"
    rooms.aggregate_method = "aggregate_rooms"
    action = BooleanFilter(field_name="has_discount", label="Фильтр по акции")
    floor = RangeFilter(field_name="floor__number", label="Фильтр по этажу")
    floor_id = NumberInFilter(label="Фильтр по этажу")
    area = RangeFilter(label="Фильтр по площади")
    price = RangeFilter(label="Фильтр по цене")
    completion_date = Filter(
        method="completion_date_filter", label="Фильтр по диапазону срока сдачи"
    )
    completion_date.specs = "get_completion_date_specs"
    completion_date.aggregate_method = "aggregate_completion_date"
    layout = NumberInFilter(label="Фильтр по планировкам")
    features = BaseInFilter(method="filter_features", label="Фильтр по особенностям")
    special_offers = BaseInFilter(field_name="specialoffer__id", label="Фильтр по акциям")
    features.specs = "get_features_specs"
    features.aggregate_method = "aggregate_features"

    special_offers.specs = "get_special_offers_specs"
    special_offers.aggregate_method = "aggregate_special_offers"

    article = CharInFilter(label="Фильтр по артиклу помещения")
    article.skip = True

    order = OrderingFilter(
        fields=("area", "price"), field_labels={"area": "Площадь", "price": "Цена"}
    )

    class Meta:
        model = Property
        fields = ()

    @staticmethod
    def rooms_filter(queryset, name, value):
        return queryset.annotate(
            rooms_value=Case(
                When(Q(rooms__gte=4), then=Value("4")),
                default=F("rooms"),
                output_field=CharField(),
            )
        ).filter(rooms_value__in=value)

    @staticmethod
    def get_rooms_specs(queryset):
        specs = [
            {"value": "0", "label": "Студия"},
            {"value": "1", "label": "1"},
            {"value": "2", "label": "2"},
            {"value": "3", "label": "3"},
            {"value": "4", "label": "4+"},
        ]
        return specs

    @staticmethod
    def aggregate_rooms(queryset):
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

    @staticmethod
    def completion_date_filter(queryset, name, value):
        try:
            from_date, to_date = value.split(",")
            from_year, from_quarter = [int(i) for i in from_date.split("-")]
            to_year, to_quarter = [int(i) for i in to_date.split("-")]
        except ValueError:
            return queryset
        return queryset.filter(
            Q(building__built_year=from_year, building__ready_quarter__gte=from_quarter)
            | Q(building__built_year=to_year, building__ready_quarter__lte=to_quarter)
            | Q(building__built_year__gt=from_year, building__built_year__lt=to_year)
        )

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

    def facets(self):
        result = super().facets()
        result.update({'count': self.qs.values_list('layout', flat=True).distinct().count()})
        return result

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
    def section_specs(queryset):
        specs = (
            queryset.annotate(label=Concat(
                Value("Секция"), Value(" "), F("section__number"), output_field=CharField()),
                              value=F("section_id"))
            .values("label", "value")
            .order_by("value")
            .distinct("value")
        )
        return specs

    @staticmethod
    def section_group_specs(queryset):
        return []

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
            queryset.filter(specialoffer__is_display=True)
            .annotate(value=F("specialoffer__id"))
            .values_list("value", flat=True)
            .order_by("value")
            .distinct("value")
        )
        return res
