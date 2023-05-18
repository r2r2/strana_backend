from __future__ import annotations

from django.db import models
from django.db.models import (Avg, Case, CharField, Count, Exists, F, Max, Min,
                              OuterRef, Q, Subquery, Value, When)
from django.db.models.functions import Concat, Greatest, Least, Lower, Upper
from django.utils.timezone import now

from buildings.constants import BuildingType
from buildings.models import Building
from common.utils import get_quarter_from_month
from mortgage.constants import MortgageType
from mortgage.models import Offer
from properties.constants import (COMMERCIAL_TYPES, FLAT_TYPES,
                                  PARKING_PANTRY_TYPES, PropertyStatus)
from properties.models import Property


class ProjectQuerySet(models.QuerySet):
    """
    Менеджер проектов
    """
    common_price_filter = Q(property__type__in=FLAT_TYPES) & Q(property__status=PropertyStatus.FREE) & Q(
        property__building__is_active=True)
    common_commercial_filter = Q(property__type__in=COMMERCIAL_TYPES) & Q(property__status=PropertyStatus.FREE) & Q(
        property__building__is_active=True)
    common_parking_filter = (Q(property__type__in=PARKING_PANTRY_TYPES)
                             & Q(property__status=PropertyStatus.FREE)
                             & Q(property__project__disable_parking=False))
    def filter_active(self) -> ProjectQuerySet:

        active = Q(active=True) & (Q(city__active=True) | Q(city__isnull=True))

        return self.filter(active)

    def annotate_min_prop_price(self) -> ProjectQuerySet:
        min_flat_price = Min(
            "property__price", filter=self.common_price_filter
        )
        min_commercial_prop_price = Min(
            "property__price", filter=(Q(property__type__in=COMMERCIAL_TYPES)
                                       & Q(status=PropertyStatus.FREE))
        )
        min_commercial_tenant_price = Min(
            "property__price", filter=(self.common_commercial_filter & Q(property__has_tenant=True))
        )
        min_commercial_business_price = Min(
            "property__price", filter=(Q(property__type__in=COMMERCIAL_TYPES)
                                       & Q(property__status=PropertyStatus.FREE)
                                       & Q(property__for_business=True))
        )

        return self.annotate(
            min_flat_price_a=min_flat_price,
            min_commercial_prop_price_a=min_commercial_prop_price,
            min_commercial_tenant_price_a=min_commercial_tenant_price,
            min_commercial_business_price_a=min_commercial_business_price,
        )

    def annotate_prop_area_range(self):
        common_property_filter = Q(property__status=PropertyStatus.FREE) & Q(property__building__is_active=True)
        min_flat_area = Min(
            "property__area", filter=common_property_filter & Q(property__type__in=FLAT_TYPES)
        )
        max_flat_area = Max(
            "property__area", filter=common_property_filter & Q(property__type__in=FLAT_TYPES)
        )
        min_commercial_prop_area = F("min_commercial_area")
        max_commercial_prop_area = F("max_commercial_area")

        return self.annotate_commercial_area().annotate(
            min_flat_area_a=min_flat_area,
            max_flat_area_a=max_flat_area,
            min_commercial_prop_area_a=min_commercial_prop_area,
            max_commercial_prop_area_a=max_commercial_prop_area,
        )

    def annotate_min_rooms_prices(self) -> ProjectQuerySet:
        qs = self.annotate(
            min_price_0=Min(
                'property__price', filter=self.common_price_filter & Q(property__rooms=0)
            ),
            min_price_1=Min(
                'property__price', filter=self.common_price_filter & Q(property__rooms=1)
            ),
            min_price_2=Min(
                'property__price', filter=self.common_price_filter & Q(property__rooms=2)
            ),
            min_price_3=Min(
                'property__price', filter=self.common_price_filter & Q(property__rooms=3)
            ),
            min_price_4=Min(
                'property__price', filter=self.common_price_filter & Q(property__rooms=4)
            ),
        )
        room_params = {
            f"flats_{rooms_count}_min_price_a": F(f"min_price_{rooms_count}") for rooms_count in range(5)
        }
        return qs.annotate(**room_params)

    def annotate_flats_count(self) -> ProjectQuerySet:
        return self.annotate(
            flats_count=Count(
                'property', filter=Q(property__type__in=FLAT_TYPES)
                                   & Q(property__status=PropertyStatus.FREE)
                                   & Q(property__building__is_active=True)
                                   & Q(property__plan__isnull=False),
                distinct=True
            )
        )

    def annotate_parking_pantry_count(self) -> ProjectQuerySet:
        return self.annotate(
            parking_pantry_count=Count(
                'property', filter=self.common_parking_filter,
                distinct=True
            ),
        )

    def annotate_commercial_count(self) -> ProjectQuerySet:
        return self.annotate(
            commercial_count=Count(
                'property', filter=Q(property__type__in=COMMERCIAL_TYPES) & Q(property__status=PropertyStatus.FREE),
                distinct=True
            ),
        )

    def annotate_commercial_prices(self) -> ProjectQuerySet:
        return self.annotate(
            min_commercial_price=Min(
                'property__price', filter=self.common_commercial_filter
            ),
            max_commercial_price=Max(
                'property__price', filter=self.common_commercial_filter
            )
        )

    def annotate_parking_pantry_area(self) -> ProjectQuerySet:
        return self.annotate(
            min_parking_area=Min(
                'property__area', filter=self.common_parking_filter
            ),
            max_parking_area=Max('property__area', filter=self.common_parking_filter)
        )

    def annotate_commercial_area(self) -> ProjectQuerySet:
        return self.annotate(
            min_commercial_area=Min(
                'property__area', filter=self.common_commercial_filter
            ),
            max_commercial_area=Max(
                'property__area', filter=self.common_commercial_filter
            )
        )

    def annotate_min_rate_offers(self) -> ProjectQuerySet:
        min_rate_offers = Subquery(
            Offer.objects.filter(
                Q(is_active=True)
                & (
                    Q(projects=OuterRef("pk"))
                    | (Q(projects__isnull=True) & Q(city=OuterRef("city")))
                    | (Q(projects__isnull=True) & Q(city__isnull=True))
                )
            )
            .annotate(min_rate=Least(Upper("rate"), Lower("rate")))
            .order_by("min_rate")
            .values("min_rate")[:1]
        )

        return self.annotate(min_rate_offers_a=min_rate_offers)

    def annotate_has_parking(self) -> ProjectQuerySet:
        from buildings.constants import BuildingType
        from buildings.models import Building

        has_parking = Exists(
            Building.objects.filter(project=OuterRef("pk"), kind=BuildingType.PARKING)
        )

        return self.annotate(has_parking=has_parking)

    def annotate_parking_pantry_price(self):
        return self.annotate(
            min_parking_pantry_price=Min(
                'property__price', filter=Q(property__type__in=PARKING_PANTRY_TYPES)
                                          & Q(property__status=PropertyStatus.FREE)
                                          & Q(property__project__disable_parking=False)
            ),
            max_parking_pantry_price=Max(
                'property__price', filter=Q(property__type__in=PARKING_PANTRY_TYPES)
                                          & Q(property__status=PropertyStatus.FREE)
                                          & Q(property__project__disable_parking=False)
            )
        )
    def annotate_has_commercial(self) -> ProjectQuerySet:
        from buildings.constants import BuildingType
        from buildings.models import Building

        has_commercial = Exists(
            Building.objects.filter(project=OuterRef("pk"), kind=BuildingType.OFFICE)
        )

        return self.annotate(has_commercial=has_commercial)

    def annotate_min_mortgage(self) -> ProjectQuerySet:
        """TODO: пока ниаслил"""
        min_flat_mortgage = Subquery(
            Offer.objects.filter(
                Q(is_active=True)
                & (
                    Q(projects=OuterRef("pk"))
                    | (Q(projects__isnull=True) & Q(city=OuterRef("city")))
                    | (Q(projects__isnull=True) & Q(city__isnull=True))
                )
                & Q(type=MortgageType.RESIDENTIAL)
            )
            .annotate(
                max_term=Greatest(Upper("term"), Lower("term")),
                max_deposit=Greatest(Upper("deposit"), Lower("deposit")),
                max_amount=Greatest(Upper("amount"), Lower("amount")),
            )
            .filter(max_amount__gte=OuterRef("min_flat_price"))
            .annotate_payment(OuterRef("min_flat_price"), F("max_deposit"), F("max_term"))
            .order_by("payment")
            .values("payment")[:1]
        )

        min_commercial_mortgage = Subquery(
            Offer.objects.filter(
                Q(is_active=True)
                & (
                    Q(projects=OuterRef("pk"))
                    | (Q(projects__isnull=True) & Q(city=OuterRef("city")))
                    | (Q(projects__isnull=True) & Q(city__isnull=True))
                )
                & Q(type=MortgageType.COMMERCIAL)
            )
            .annotate(
                max_term=Greatest(Upper("term"), Lower("term")),
                max_deposit=Greatest(Upper("deposit"), Lower("deposit")),
                max_amount=Greatest(Upper("amount"), Lower("amount")),
            )
            .filter(max_amount__gte=OuterRef("min_commercial_prop_price"))
            .annotate_payment(
                OuterRef("min_commercial_prop_price"), F("max_deposit"), F("max_term")
            )
            .order_by("payment")
            .values("payment")[:1]
        )

        return self.annotate(
            min_flat_mortgage_a=min_flat_mortgage, min_commercial_mortgage_a=min_commercial_mortgage
        )

    def annotate_bank_logo(self) -> ProjectQuerySet:

        bank_logo_1 = Subquery(
            Offer.objects.select_related("bank")
            .filter(
                Q(is_active=True)
                & (
                    Q(projects=OuterRef("pk"))
                    | (Q(projects__isnull=True) & Q(city=OuterRef("city")))
                    | (Q(projects__isnull=True) & Q(city__isnull=True))
                )
            )
            .order_by("order")
            .values("bank__logo")[:1]
        )

        bank_logo_2 = Subquery(
            Offer.objects.select_related("bank")
            .filter(
                Q(is_active=True)
                & (
                    Q(projects=OuterRef("pk"))
                    | (Q(projects__isnull=True) & Q(city=OuterRef("city")))
                    | (Q(projects__isnull=True) & Q(city__isnull=True))
                )
            )
            .order_by("-order")
            .values("bank__logo")[:1]
        )

        return self.annotate(bank_logo_1_a=bank_logo_1, bank_logo_2_a=bank_logo_2)

    def annotate_label_with_completion(self) -> ProjectQuerySet:
        """Аннотация проекта скором готовности ближайшего корпуса, для фильтр квартир"""

        n = now()
        quarter = get_quarter_from_month(n.month)

        label_with_completion = Subquery(
            Building.objects.annotate_flats_count()
            .filter(
                Q(
                    project=OuterRef("id"),
                    is_active=True,
                    kind=BuildingType.RESIDENTIAL,
                    flats_count__gt=0,
                )
                & (Q(built_year__gt=n.year) | Q(built_year__gte=n.year, ready_quarter__gte=quarter))
            )
            .annotate(
                first_str=Case(
                    When(Q(project__show_close=True), then=Value("(ближ. ")), default=Value("(")
                )
            )
            .annotate(
                label=Concat(
                    F("first_str"),
                    F("ready_quarter"),
                    Value(" кв. "),
                    F("built_year"),
                    Value(")"),
                    output_field=CharField(),
                )
            )
            .order_by("built_year", "ready_quarter")
            .values("label")[:1]
        )

        return self.annotate(label_with_completion_a=label_with_completion)

    def annotate_flats_prices(self):
        property_filter = Q(
            property__type__in=FLAT_TYPES,
            property__status=PropertyStatus.FREE,
            property__building__is_active=True,
        )
        return self.annotate(
            min_flat_price_penny=Min(
                "property__price", filter=property_filter, output_field=models.IntegerField()
            )
            * Value(100),
            max_flat_price_penny=Max(
                "property__price", filter=property_filter, output_field=models.IntegerField()
            )
            * Value(100),
            avg_flat_price_penny=Avg(
                "property__price", filter=property_filter, output_field=models.IntegerField()
            )
            * Value(100),
        )


class ProjectManager(models.Manager):
    """Менеджер с методом для выполнения запроса по умолчанию.

    Так же добавлены другие методы с аннотированными полями для обратной совместимости с функционалом панели менеджера.
    """
    def get_queryset(self) -> ProjectQuerySet:
        qs = ProjectQuerySet(self.model, using=self._db)
        return qs

    def annotate_prop_area_range(self):
        return self.get_queryset().annotate_prop_area_range()

    def annotate_min_rooms_prices(self):
        return self.get_queryset().annotate_min_rooms_prices()

    def annotate_commercial_count(self):
        return self.get_queryset().annotate_commercial_count()

    def annotate_commercial_area(self):
        return self.get_queryset().annotate_commercial_area()

    def filter_active(self):
        return self.get_queryset().filter_active()

    def annotate_parking_pantry_area(self):
        return self.get_queryset().annotate_parking_pantry_area()

    def annotate_parking_pantry_price(self):
        return self.get_queryset().annotate_parking_pantry_price()

    def annotate_parking_pantry_count(self):
        return self.get_queryset().annotate_parking_pantry_count()

    def annotate_has_parking(self):
        return self.get_queryset().annotate_has_parking()

    def annotate_bank_logo(self):
        return self.get_queryset().annotate_bank_logo()

    def annotate_min_mortgage(self):
        return self.get_queryset().annotate_min_mortgage()

    def annotate_flats_count(self):
        return self.get_queryset().annotate_flats_count()

    def annotate_label_with_completion(self):
        return self.get_queryset().annotate_label_with_completion()

    def annotate_flats_prices(self):
        return self.get_queryset().annotate_flats_prices()

    def annotate_min_rate_offers(self):
        return self.get_queryset().annotate_min_rate_offers()

    def annotate_min_prop_price(self):
        return self.get_queryset().annotate_min_prop_price()

    def annotate_has_commercial(self):
        return self.get_queryset().annotate_has_commercial()

    def annotate_commercial_prices(self):
        return self.get_queryset().annotate_commercial_prices()


