from __future__ import annotations
from django.db.models import (
    QuerySet,
    Count,
    Q,
    F,
    Min,
    Subquery,
    OuterRef,
    IntegerField,
    Max,
    Case,
    When,
    ExpressionWrapper,
)
from django.utils.timezone import now
from django.db.models.functions import ExtractDay, ExtractYear, ExtractMonth, Cast
from properties.constants import PropertyType, PropertyStatus, COMMERCIAL_TYPES, FLAT_TYPES


class BuildingQuerySet(QuerySet):
    """
    Менеджер корпусов
    """

    def filter_active(self):
        return self.filter(is_active=True)

    def annotate_min_prices(self) -> BuildingQuerySet:
        from properties.models import Property

        room_params = {
            f"flats_{rooms_count}_min_price_a": Subquery(
                Property.objects.filter(
                    type__in=FLAT_TYPES,
                    rooms=rooms_count,
                    status=PropertyStatus.FREE,
                    building=OuterRef("pk"),
                )
                .values("price")
                .order_by("price")[:1]
            )
            for rooms_count in range(5)
        }

        return self.annotate(**room_params)

    def annotate_total_floor(self) -> BuildingQuerySet:
        from buildings.models import Floor

        total_floor = Subquery(
            Floor.objects.filter(section__building=OuterRef("pk"))
            .values("number")
            .annotate(max=Max("number"))
            .values("max")
            .order_by("-max")[:1],
            output_field=IntegerField(),
        )

        return self.annotate(total_floor=total_floor)

    def annotate_flats_count(self) -> BuildingQuerySet:

        flats_count = Count(
            "property",
            filter=Q(
                property__type__in=FLAT_TYPES,
                property__status=PropertyStatus.FREE,
                property__building__is_active=True,
                property__plan__isnull=False
            ),
        )

        return self.annotate(flats_count=flats_count)

    def annotate_parking_count(self) -> BuildingQuerySet:

        parking_count = Count(
            "property",
            filter=Q(property__type=PropertyType.PARKING, property__status=PropertyStatus.FREE),
        )

        return self.annotate(parking_count=parking_count)

    def annotate_pantry_count(self) -> BuildingQuerySet:

        pantry_count = Count(
            "property",
            filter=Q(property__type=PropertyType.PANTRY, property__status=PropertyStatus.FREE),
        )

        return self.annotate(pantry_count=pantry_count)

    def annotate_commercial_count(self) -> BuildingQuerySet:

        commercial_count = Count(
            "property",
            filter=Q(property__type__in=COMMERCIAL_TYPES, property__status=PropertyStatus.FREE),
        )
        return self.annotate(commercial_count=commercial_count)

    def annotate_current_level(self) -> BuildingQuerySet:

        dates_not_null = Q(start_date__isnull=False, fact_date__isnull=False)
        first = ExpressionWrapper(now().date() - F("start_date"), IntegerField())
        second = ExpressionWrapper(ExtractDay(F("fact_date") - F("start_date")), IntegerField())

        current_level = Case(
            When(dates_not_null & Q(fact_date__gt=F("start_date")), then=first / second * 100),
            default=F("current_level"),
            output_field=IntegerField(),
        )

        return self.annotate(current_level_a=current_level)._annotate_current_level()

    def _annotate_current_level(self) -> BuildingQuerySet:
        current_level = Case(When(current_level_a__gt=100, then=100), default=F("current_level_a"))
        return self.annotate(current_level_a=current_level)

    def annotate_finish_dates(self) -> BuildingQuerySet:

        built_year = Case(
            When(finish_date__isnull=False, then=ExtractYear("finish_date")),
            default=F("built_year"),
            output_field=IntegerField(),
        )

        ready_quarter = Case(
            When(
                finish_date__isnull=False,
                then=Cast(ExtractMonth("finish_date") - 1, IntegerField()) / 3 + 1,
            ),
            default=F("ready_quarter"),
            output_field=IntegerField(),
        )

        return self.annotate(built_year_a=built_year, ready_quarter_a=ready_quarter)


class SectionQuerySet(QuerySet):
    """
    Менеджер секций
    """

    def annotate_min_prices(self) -> SectionQuerySet:
        from properties.models import Property

        room_params = {
            f"flats_{rooms_count}_min_price_a": Subquery(
                Property.objects.filter(
                    type__in=FLAT_TYPES,
                    rooms=rooms_count,
                    status=PropertyStatus.FREE,
                    section=OuterRef("pk"),
                )
                .values("price")
                .order_by("price")[:1]
            )
            for rooms_count in range(5)
        }

        return self.annotate(**room_params)

    def annotate_total_floor(self) -> SectionQuerySet:
        from buildings.models import Floor

        total_floor = Subquery(
            Floor.objects.filter(section=OuterRef("pk"))
            .values("section")
            .annotate(count=Count("pk"))
            .values("count"),
            output_field=IntegerField(),
        )

        return self.annotate(total_floor=total_floor)

    def annotate_flats_count(self) -> SectionQuerySet:

        flats_count = Count(
            "property",
            filter=Q(
                property__type__in=FLAT_TYPES,
                property__status=PropertyStatus.FREE,
                property__building__is_active=True,
                property__plan__isnull=False
            ),
        )

        return self.annotate(flats_count=flats_count)


class FloorQuerySet(QuerySet):
    """
    Менеджер этажей
    """

    def annotate_min_prices(self) -> FloorQuerySet:
        from properties.models import Property

        room_params = {
            f"flats_{rooms_count}_min_price_a": Subquery(
                Property.objects.filter(
                    type__in=FLAT_TYPES,
                    rooms=rooms_count,
                    status=PropertyStatus.FREE,
                    floor=OuterRef("pk"),
                )
                .values("price")
                .order_by("price")[:1]
            )
            for rooms_count in range(5)
        }

        return self.annotate(**room_params)

    def annotate_flats_min_price(self) -> FloorQuerySet:

        flats_min_price = Min(
            "property__price",
            filter=Q(property__type__in=FLAT_TYPES, property__status=PropertyStatus.FREE),
        )

        return self.annotate(flats_min_price=flats_min_price)

    def annotate_flats_count(self) -> FloorQuerySet:

        flats_count = Count(
            "property",
            filter=Q(
                property__type__in=FLAT_TYPES,
                property__status=PropertyStatus.FREE,
                property__building__is_active=True,
                property__plan__isnull=False
            ),
        )

        return self.annotate(flats_count=flats_count)

    def annotate_commercial_count(self) -> FloorQuerySet:

        commercial_count = Count(
            "property",
            filter=Q(property__type__in=COMMERCIAL_TYPES, property__status=PropertyStatus.FREE),
        )

        return self.annotate(commercial_count=commercial_count)

    def annotate_parking_count(self) -> FloorQuerySet:

        parking_count = Count(
            "property",
            filter=Q(property__type=PropertyType.PARKING, property__status=PropertyStatus.FREE),
        )

        return self.annotate(parking_count=parking_count)

    def annotate_pantry_count(self) -> FloorQuerySet:

        pantry_count = Count(
            "property",
            filter=Q(property__type=PropertyType.PANTRY, property__status=PropertyStatus.FREE),
        )

        return self.annotate(pantry_count=pantry_count)
