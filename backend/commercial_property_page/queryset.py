from __future__ import annotations
from django.db.models import Q, QuerySet, Subquery, OuterRef
from django.db.models.functions import Least, Lower, Upper
from mortgage.constants import MortgageType
from mortgage.models import Offer
from properties.constants import PropertyType
from properties.models import Property


class CommercialPropertyPageQueryset(QuerySet):
    """
    Менеджер страницы коммерческой недвижимости
    """

    def annotate_area_range(self) -> CommercialPropertyPageQueryset:
        min_area = Subquery(
            Property.objects.filter(project__city=OuterRef("city"), type=PropertyType.COMMERCIAL)
            .order_by("area")
            .values("area")[:1]
        )

        max_area = Subquery(
            Property.objects.filter(project__city=OuterRef("city"), type=PropertyType.COMMERCIAL)
            .order_by("-area")
            .values("area")[:1]
        )

        min_area_tenant = Subquery(
            Property.objects.filter(
                project__city=OuterRef("city"), type=PropertyType.COMMERCIAL, has_tenant=True
            )
            .order_by("area")
            .values("area")[:1]
        )

        max_area_tenant = Subquery(
            Property.objects.filter(
                project__city=OuterRef("city"), type=PropertyType.COMMERCIAL, has_tenant=True
            )
            .order_by("-area")
            .values("area")[:1]
        )

        return self.annotate(
            min_area=min_area,
            max_area=max_area,
            min_area_tenant=min_area_tenant,
            max_area_tenant=max_area_tenant,
        )

    def annotate_min_price(self) -> CommercialPropertyPageQueryset:

        min_price = Subquery(
            Property.objects.filter(project__city=OuterRef("city"), type=PropertyType.COMMERCIAL)
            .order_by("price")
            .values("price")[:1]
        )

        min_price_tenant = Subquery(
            Property.objects.filter(
                project__city=OuterRef("city"), type=PropertyType.COMMERCIAL, has_tenant=True
            )
            .order_by("price")
            .values("price")[:1]
        )

        return self.annotate(min_price=min_price, min_price_tenant=min_price_tenant)

    def annotate_min_rate_offers(self):
        min_rate_offers = Subquery(
            Offer.objects.filter(
                Q(is_active=True)
                & Q(type=MortgageType.COMMERCIAL)
                & (Q(city=OuterRef("city")) | Q(city__isnull=True))
            )
            .annotate(min_rate=Least(Upper("rate"), Lower("rate")))
            .order_by("min_rate")
            .values("min_rate")[:1]
        )

        return self.annotate(min_rate_offers=min_rate_offers)
