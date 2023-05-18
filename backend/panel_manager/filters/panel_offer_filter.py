import math
from django.db.models import F, Q, Max, Min
from django_filters import ChoiceFilter, CharFilter, BaseInFilter
from graphql_relay import from_global_id

from mortgage.constants import MortgageType
from mortgage.models import OfferPanel
from properties.constants import PropertyType
from properties.models import Property
from common.filters import FacetFilterSet, FloatFilter, IntegerFilter


class PanelOfferFilterSet(FacetFilterSet):
    """
    Фильтр предложений
    """
    type = ChoiceFilter(field_name="type", choices=MortgageType.choices, label="Фильтр по типу")
    program = BaseInFilter(field_name="program", label="Фильтр по программе")
    deposit = FloatFilter(field_name="deposit", lookup_expr="contains", label="Фильтр по депозиту")
    rate = FloatFilter(field_name="rate", lookup_expr="contains", label="Фильтр по ставке")
    term = FloatFilter(field_name="term", lookup_expr="contains", label="Фильтр по сроку")
    price = IntegerFilter(method="price_filter", label="Фильтр по цене")
    project = CharFilter(field_name="projects__id", label="Фильтр по проекту")
    city = BaseInFilter(field_name="city", label="Фильтр по городу")

    type.specs = "get_type_specs"
    project.specs = "get_project_specs"
    program.specs = "get_program_specs"

    project.aggregate_method = "project_aggregate"
    type.aggregate_method = "type_aggregate"

    class Meta:
        model = OfferPanel
        fields = ("type", "program", "deposit", "rate", "term", "price", "project", "city")

    def facets(self):
        self.queryset = self.queryset.filter(is_active=True)
        facets = super().facets()
        queryset = Property.objects.filter_active()
        type = self.form.cleaned_data.get("type")
        city = self.form.cleaned_data.get("city")

        residential_query = Q(type__in=[PropertyType.FLAT, PropertyType.COMMERCIAL_APARTMENT])
        commercial_query = Q(type__in=[PropertyType.COMMERCIAL, PropertyType.COMMERCIAL_APARTMENT])
        if type:
            if type == "residential":
                queryset = queryset.filter(residential_query)
            else:
                queryset = queryset.filter(commercial_query)
        else:
            queryset = queryset.filter(residential_query | commercial_query)
        if city:
            _, _id = from_global_id(city)
            queryset = queryset.filter(Q(project__city=_id) | Q(project__city__isnull=True))
        values = queryset.aggregate(min=Min("price"), max=Max("price"))
        facets["facets"].append(
            {
                "name": "price",
                "range": {
                    "min": values.get("min", 0) and math.ceil(values.get("min", 0)),
                    "max": values.get("max", 90) and math.floor(values.get("max", 90)),
                },
            }
        )
        deposit = list(filter(lambda x: x.get("name") == "deposit", facets["facets"]))
        deposit[0]["range"]["max"] = None if deposit[0]["range"]["max"] is None else 90
        return facets

    def specs(self):
        self.queryset = self.queryset.filter(is_active=True)
        self.queryset = self.qs
        specs = super().specs()
        values = (
            Property.objects.filter_active()
            .filter(
                Q(type=PropertyType.FLAT)
                | Q(type__in=[PropertyType.COMMERCIAL, PropertyType.COMMERCIAL_APARTMENT])
            )
            .aggregate(min=Min("price"), max=Max("price"))
        )
        specs.append(
            {
                "name": "price",
                "range": {
                    "min": values.get("min", 0) and math.ceil(values.get("min", 0)),
                    "max": values.get("max", 90) and math.floor(values.get("max", 90)),
                },
            }
        )
        deposit = list(filter(lambda x: x.get("name") == "deposit", specs))
        deposit[0]["range"]["max"] = None if deposit[0]["range"]["max"] is None else 90
        return specs

    def price_filter(self, queryset, name, value):
        if not value:
            return

        deposit = self.data.get("deposit_sum")
        if deposit:
            return queryset.annotate_filter_price(value, deposit).filter(
                Q(amount__contains=F("price_f")) | Q(amount__isnull=True)
            )
        return queryset.filter(Q(amount__contains=value) | Q(amount__isnull=True))

    @staticmethod
    def get_type_specs(queryset):
        qs = (
            queryset.distinct(Q(type__isnull=True) | Q(type=""))
            .order_by("type")
            .values_list("type", flat=True)
            .distinct()
        )
        specs = [{"value": value, "label": dict(MortgageType.choices)[value]} for value in qs]
        return specs

    @staticmethod
    def get_project_specs(queryset):
        res = (
            queryset.filter(projects__slug__isnull=False)
            .annotate(label=F("projects__name"), value=F("projects__id"))
            .values("label", "value")
            .order_by("projects__order", "projects__id")
            .distinct("projects__order", "projects__id")
        )
        specs = [{"label": i["label"], "value": i["value"]} for i in res]
        return specs

    @staticmethod
    def get_program_specs(queryset):
        res = (
            queryset.filter(program__isnull=False)
            .values("program__id", "program__name", "program__order")
            .order_by("program__id", "program__name", "program__order")
            .distinct("program__id", "program__name", "program__order")
        )
        specs = [
            {
                "label": i["program__name"],
                "value": i["program__id"],
                "order": i["program__order"],
            }
            for i in res
        ]
        return specs

    @staticmethod
    def type_aggregate(queryset):
        qs = (
            queryset.distinct(Q(type__isnull=True) | Q(type=""))
            .order_by("type")
            .values_list("type", flat=True)
            .distinct()
        )
        aggregate = [value for value in qs]
        return aggregate

    @staticmethod
    def project_aggregate(queryset):
        res = (
            queryset.filter(projects__slug__isnull=False)
            .order_by()
            .values_list("projects__id", flat=True)
            .distinct()
        )
        aggregate = [elem for elem in res]
        return aggregate
