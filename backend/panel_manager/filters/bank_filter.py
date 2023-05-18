
from graphene_django.filter import GlobalIDFilter
from django.db.models import Q, Min, Max
from graphql_relay import from_global_id
import math
from mortgage.models import Bank
from common.filters import FacetFilterSet, FloatFilter
from properties.constants import PropertyType
from properties.models import Property


class BankFilter(FacetFilterSet):
    """Класс фильтр банков.

    Работает аналогично фильтрации предложений.
    """
    program = GlobalIDFilter(field_name="offerpanel__program", label="Фильтр по программе")
    deposit = FloatFilter(field_name="offerpanel__deposit", lookup_expr="contains", label="Фильтр по депозиту")
    rate = FloatFilter(field_name="offerpanel__rate", lookup_expr="contains", label="Фильтр по ставке")
    term = FloatFilter(field_name="offerpanel__term", lookup_expr="contains", label="Фильтр по сроку")

    class Meta:
        model = Bank
        fields = ("offerpanel", "deposit", "term")

    def facets(self):
        self.queryset = self.queryset.filter(offerpanel__is_active=True).distinct()
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
        deposit[0]["range"]["max"] = None if deposit[0]["range"].get("max") is None else 90
        return facets

    def specs(self):
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
        deposit[0]["range"]["max"] = None if deposit[0]["range"].get("max") is None else 90
        return specs
