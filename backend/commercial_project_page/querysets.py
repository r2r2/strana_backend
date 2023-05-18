from __future__ import annotations
from django.db.models.functions import Least, Upper, Lower
from django.db.models import (
    Q,
    F,
    Count,
    QuerySet,
    IntegerField,
    FloatField,
    Subquery,
    OuterRef,
    ExpressionWrapper,
)

from mortgage.models import Offer
from mortgage.constants import MortgageType
from properties.models import Property
from properties.constants import PropertyStatus, COMMERCIAL_TYPES


class CommercialProjectPageQuerySet(QuerySet):
    def annotate_min_rate(self) -> CommercialProjectPageQuerySet:

        min_rate = Subquery(
            Offer.objects.filter(
                is_active=True, type=MortgageType.COMMERCIAL, projects=OuterRef("project")
            )
            .annotate(min_rate=Least(Upper("rate"), Lower("rate"), output_field=FloatField()))
            .order_by("min_rate")
            .values("min_rate")[:1]
        )

        return self.annotate(min_rate=min_rate)

    def annotate_min_commercial_property_price(self) -> CommercialProjectPageQuerySet:

        min_commercial_property_price = Subquery(
            Property.objects.filter(
                status=PropertyStatus.FREE, type__in=COMMERCIAL_TYPES, project=OuterRef("project")
            )
            .order_by("price")
            .values("price")[:1]
        )
        return self.annotate(min_commercial_property_price=min_commercial_property_price)

    def annotate_min_initial_fee(self) -> CommercialProjectPageQuerySet:

        min_offer_deposit = Subquery(
            Offer.objects.filter(
                is_active=True, type=MortgageType.COMMERCIAL, projects=OuterRef("project")
            )
            .annotate(
                min_deposit=Least(Upper("deposit"), Lower("deposit"), output_field=FloatField())
            )
            .order_by("min_deposit")
            .values("min_deposit")[:1]
        )

        min_initial_fee = ExpressionWrapper(
            (min_offer_deposit / 100) * F("min_commercial_property_price"),
            output_field=IntegerField(),
        )

        return self.annotate(min_initial_fee=min_initial_fee)
