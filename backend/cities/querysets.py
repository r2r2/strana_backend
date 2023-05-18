from __future__ import annotations

from django.db.models import (BooleanField, Case, DecimalField, Exists,
                              ExpressionWrapper, F, Manager, OuterRef, Q,
                              QuerySet, Subquery, Value, When)

from mortgage.constants import MortgageType
from properties.constants import COMMERCIAL_TYPES, FLAT_TYPES, PropertyStatus


class CityQuerySet(QuerySet):
    """
    Менеджер городов
    """

    def annotate_min_mortgages(self) -> CityQuerySet:
        from mortgage.models import Offer

        min_mortgage_commercial = Subquery(
            Offer.objects.filter(city=OuterRef("pk"), type=MortgageType.COMMERCIAL, is_active=True)
            .values("rate")
            .order_by("rate")[:1]
        )
        offers = Offer.objects.filter(city=OuterRef("pk"), type=MortgageType.RESIDENTIAL, is_active=True)
        min_mortgage_residential = Subquery(
            offers
            .values("rate")
            .order_by("rate")[:1]
        )
        min_mortgage_residential_standard = Subquery(
            offers
            .filter(program__name="Стандартная программа")
            .values("rate")
            .order_by("rate")[:1]
        )
        min_mortgage_residential_support = Subquery(
            offers
            .filter(program__name="Господдержка")
            .values("rate")
            .order_by("rate")[:1]
        )
        min_mortgage_residential_family = Subquery(
            offers
                .filter(program__name="Семейная ипотека")
                .values("rate")
                .order_by("rate")[:1]
        )
        return self.annotate(
            min_mortgage_commercial_a=min_mortgage_commercial,
            min_mortgage_residential_a=min_mortgage_residential,
            min_mortgage_residential_standard_a=min_mortgage_residential_standard,
            min_mortgage_residential_support_a=min_mortgage_residential_support,
            min_mortgage_residential_family_a=min_mortgage_residential_family
        )

    def annotate_min_prices(self) -> CityQuerySet:
        from properties.models import Property

        room_params = {
            f"flats_{rooms_count}_min_price_a": Subquery(
                Property.objects.filter(
                    type__in=FLAT_TYPES,
                    rooms=rooms_count,
                    status=PropertyStatus.FREE,
                    project__city=OuterRef("pk"),
                    building__is_active=True,
                )
                .values("price")
                .order_by("price")[:1]
            )
            for rooms_count in range(5)
        }

        return self.annotate(**room_params)

    def annotate_min_commercial_price(self) -> CityQuerySet:
        from properties.models import Property

        min_commercial_price = Subquery(
            Property.objects.filter(
                type__in=COMMERCIAL_TYPES,
                status=PropertyStatus.FREE,
                project__city=OuterRef("pk"),
                building__is_active=True,
            )
            .values("price")
            .order_by("price")[:1]
        )

        min_commercial_price_divided = ExpressionWrapper(
            F("min_commercial_price_a") / Value(1000000, output_field=DecimalField()),
            output_field=DecimalField(),
        )

        return self.annotate(
            min_commercial_price_a=min_commercial_price,
            min_commercial_price_divided_a=min_commercial_price_divided,
        )

    def annotate_commercial_area_ranges(self) -> CityQuerySet:
        from properties.models import Property

        min_commercial_area = Subquery(
            Property.objects.filter(
                type__in=COMMERCIAL_TYPES,
                status=PropertyStatus.FREE,
                project__city=OuterRef("pk"),
                building__is_active=True,
            )
            .values("area")
            .order_by("area")[:1]
        )

        max_commercial_area = Subquery(
            Property.objects.filter(
                type__in=COMMERCIAL_TYPES,
                status=PropertyStatus.FREE,
                project__city=OuterRef("pk"),
                building__is_active=True,
            )
            .values("area")
            .order_by("-area")[:1]
        )

        return self.annotate(
            min_commercial_area_a=min_commercial_area, max_commercial_area_a=max_commercial_area
        )

    def annotate_is_commercial(self) -> CityQuerySet:
        from commercial_property_page.models import CommercialPropertyPage
        from projects.models import Project

        has_commercial_page = Exists(CommercialPropertyPage.objects.filter(city=OuterRef("pk")))
        is_commercial_page_hidden = Exists(
            CommercialPropertyPage.objects.filter(city=OuterRef("pk"), is_page_hidden=True)
        )

        has_commercial_project = Exists(
            Project.objects.filter(is_commercial=True, city=OuterRef("pk"))
        )

        is_commercial = Case(
            When(Q(has_commercial_page=True) & Q(has_commercial_project=True), then=True),
            default=False,
            output_field=BooleanField(),
        )

        return self.annotate(
            has_commercial_page=has_commercial_page,
            is_commercial_page_hidden=is_commercial_page_hidden,
            has_commercial_project=has_commercial_project,
            is_commercial=is_commercial,
        )

    def filter_is_commercial(self) -> CityQuerySet:

        is_commercial = True

        return self.filter(is_commercial=is_commercial)

    def annotate_has_active_projects(self) -> CityQuerySet:
        from projects.models import Project

        has_active_projects = Exists(Project.objects.filter(city=OuterRef("pk"), active=True))

        return self.annotate(has_active_projects=has_active_projects)


class CityManager(Manager):
    def get_queryset(self):
        qs =  CityQuerySet(self.model, using=self._db)
        return qs.prefetch_related("project_set", "commercialpropertypage_set")

    def annotate_min_mortgages(self):
        return self.get_queryset().annotate_min_mortgages()

    def annotate_min_prices(self):
        return self.get_queryset().annotate_min_prices()

    def annotate_min_commercial_price(self):
        return self.get_queryset().annotate_min_commercial_price()

    def annotate_is_commercial(self):
        return self.get_queryset().annotate_is_commercial()

    def filter_is_commercial(self):
        return self.get_queryset().filter_is_commercial()

    def annotate_has_active_projects(self):
        return self.get_queryset().annotate_has_active_projects()

