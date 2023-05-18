from __future__ import annotations

from decimal import Decimal

from django.db.models import (BooleanField, Case, CharField, Count,
                              DecimalField, Exists, ExpressionWrapper, F,
                              IntegerField, Max, Min, OuterRef, Q, QuerySet,
                              Subquery, Value, When, Window)
from django.db.models.functions import (Concat, FirstValue, Greatest, Least,
                                        Lower, Upper)
from django.utils.timezone import now

from auction.models import Auction
from buildings.models import Building
from common.models import ActiveQuerySet

from .constants import FeatureType, PropertyStatus, PropertyType


class PropertyAndLayoutQuerySet(QuerySet):
    """Менеджер с общими методами для объектов собственности и планировок"""

    def annotate_furnish_price(self) -> PropertyQuerySet:

        furnish_price = ExpressionWrapper(
            F("original_price") + (F("furnish_price_per_meter") * (F("no_balcony_and_terrace_area"))),
            output_field=IntegerField()
        )

        return self.annotate(furnish_price=furnish_price)

    def annotate_furnish_price_comfort(self) -> PropertyQuerySet:

        furnish_price_comfort = ExpressionWrapper(
            F("original_price") + (F("furnish_comfort_price_per_meter") * (F("no_balcony_and_terrace_area"))),
            output_field=IntegerField()
        )

        return self.annotate(furnish_price_comfort=furnish_price_comfort)

    def annotate_furnish_price_business(self) -> PropertyQuerySet:

        furnish_price_business = ExpressionWrapper(
            F("original_price") + (F("furnish_business_price_per_meter") * (F("no_balcony_and_terrace_area"))),
            output_field=IntegerField()
        )

        return self.annotate(furnish_price_business=furnish_price_business)

    def annotate_furnish_kitchen_price(self) -> PropertyQuerySet:

        furnish_kitchen_price = ExpressionWrapper(
            F("furnish_price") + F("kitchen_price"),
            output_field=IntegerField()
        )

        return self.annotate(furnish_kitchen_price=furnish_kitchen_price)

    def annotate_furnish_furniture_price(self) -> PropertyQuerySet:

        furnish_furniture_price = ExpressionWrapper(
            F("furnish_price") + F("furniture_price"),
            output_field=IntegerField()
        )

        return self.annotate(furnish_furniture_price=furnish_furniture_price)

    def annotate_furnish_kitchen_furniture_price(self) -> PropertyQuerySet:

        furnish_kitchen_furniture_price = ExpressionWrapper(
            F("furnish_price") + F("furniture_price") + F("kitchen_price"),
            output_field=IntegerField()
        )

        return self.annotate(furnish_kitchen_furniture_price=furnish_kitchen_furniture_price)

    def annotate_first_payment(self) -> PropertyAndLayoutQuerySet:
        min_deposit = Value(10, output_field=IntegerField())

        first_payment = ExpressionWrapper(
            F("price") * F("min_deposit") / 100, output_field=IntegerField()
        )

        return self.annotate(min_deposit=min_deposit, first_payment=first_payment)

    def annotate_mortgage_type(self) -> PropertyAndLayoutQuerySet:
        from mortgage.constants import MortgageType

        mortgage_type = Case(
            When(
                type=PropertyType.FLAT,
                then=Value(MortgageType.RESIDENTIAL, output_field=CharField()),
            ),
            default=Value(MortgageType.COMMERCIAL, output_field=CharField()),
        )

        return self.annotate(mortgage_type=mortgage_type)


class PropertyQuerySet(PropertyAndLayoutQuerySet):
    """
    Менеджер объектов собственности
    """

    def order_plan(self) -> PropertyQuerySet:

        plan_exists = Case(When(plan="", then=False), default=True, output_field=BooleanField())

        return self.annotate(plan_exists=plan_exists).order_by("-plan_exists", "id")

    def filter_active(self, include_booked=False) -> PropertyQuerySet:

        filter = (
            Q(building__is_active=True)
            & Q(project__active=True)
            & (Q(project__city__active=True) | Q(project__city__isnull=True))
        )
        if include_booked:
            filter &= Q(status__in=[PropertyStatus.FREE, PropertyStatus.BOOKED])
        else:
            filter &= Q(status=PropertyStatus.FREE)

        return self.filter(filter)

    def filter_enabled_parkings(self):
        return self.filter(project__disable_parking=False)

    def annotate_is_favorite(self, favorites) -> PropertyQuerySet:

        is_favorite = Case(
            When(id__in=favorites, then=True), default=False, output_field=BooleanField()
        )

        return self.annotate(is_favorite=is_favorite)

    def annotate_has_discount(self) -> PropertyQuerySet:
        time = now()

        has_discount = Case(
            When(
                Q(promo_start__lte=time) & Q(promo_end__isnull=True)
                | Q(promo_start__lte=time) & Q(promo_end__gte=time)
                | Q(promo_start__isnull=True) & Q(promo_end__gte=time)
                | Q(original_price__gt=F("price")),
                then=True,
            ),
            default=False,
            output_field=BooleanField(),
        )

        return self.annotate(has_discount=has_discount)

    def filter_similar_flats(self, flat) -> PropertyQuerySet:

        similar_flats = (
            self.filter(building=flat.building, rooms=flat.rooms)
            .exclude(pk=flat.pk)
            .annotate(
                base_price=Value(flat.price, output_field=DecimalField()),
                base_area=Value(flat.area, output_field=DecimalField()),
            )
        )

        return similar_flats

    def filter_similar_commercial_spaces(self, commercial_space) -> PropertyQuerySet:

        similar_commercial_spaces = (
            self.filter(
                project=commercial_space.project,
                area__lte=commercial_space.area * Decimal(1.25),
                area__gte=commercial_space.area * Decimal(0.75),
            )
            .exclude(pk=commercial_space.pk)
            .annotate(
                base_price=Value(commercial_space.price, output_field=DecimalField()),
                base_area=Value(commercial_space.area, output_field=DecimalField()),
            )
        )

        return similar_commercial_spaces

    def aggregate_flat_stats(self) -> PropertyQuerySet:

        min_price = Min("price")

        max_price = Max("price")

        return self.aggregate(min_price=min_price, max_price=max_price)

    def filter_feed(self, feed) -> PropertyQuerySet:
        """Фильтрация объектов собственности для фидов."""
        allowed_statuses = [PropertyStatus.FREE]

        if feed.include_booked:
            allowed_statuses.append(PropertyStatus.BOOKED)

        return self.filter(
            status__in=allowed_statuses, building__in=feed.buildings.all(), type=feed.property_type
        ).distinct("id")

    def annotate_feed_admin(self) -> PropertyQuerySet:
        return self.select_related("section__building__project", "floor")

    def annotate_feed(self) -> PropertyQuerySet:
        """Аннотация дополнительными полями для фидов."""
        qs = self.select_related(
            "floor",
            "section",
            "building",
            "project",
            "project__city",
            "project__city__site",
            "project__metro",
            "project__metro__line",
        ).prefetch_related("project__gallery_slides")
        qs = qs.annotate(
            avito_object_type=Case(
                When(purposes__in=[1, 3, 4, 11, 22, 17, 21, 25], then=Value("Торговое помещение")),
                When(purposes__in=[27], then=Value("Складское помещение")),
                default=Value("Помещение свободного назначения"),
                output_field=CharField()
            ),
            avito_decoration=Case(
                When(Q(facing=False) | Q(furnish_set__isnull=True) | Q(furnish_set__in=[6]), then=Value("Без отделки")),
                When(furnish_set__in=[23], then=Value("Офисная")),
                default=Value("Чистовая"),
                output_field=CharField()
            ),
            cian_property_type=Case(
                When(purposes__in=[27], then=Value("warehouse")),
                When(purposes__in=[1, 3, 4, 11, 17, 21, 22, 25], then=Value("shoppingArea")),
                default=Value("freeAppointment"),
                output_field=CharField()
            ),
            yandex_commercial_type=Case(
                When(purposes__in=[4, 5, 6, 18, 19], then=Value("public catering")),
                When(purposes__in=[1, 3, 11, 22, 23, 17, 21, 25], then=Value("retail")),
                When(purposes__in=[27], then=Value("warehouse")),
                default=Value("free purpose"),
                output_field=CharField()
            ),
            address=Case(
                When(Q(building__address__isnull=False) | Q(building__address=""), then=F("building__address")),
                default=F("building__project__address"),
                output_field=CharField()
            )
        )
        return qs

    def filter_current_site(self, site) -> PropertyQuerySet:

        filter = Q(project__city__isnull=True) | Q(project__city__site=site)

        return self.filter(filter)

    def annotate_rooms_type(self) -> PropertyQuerySet:

        rooms_type = Case(
            When(Q(rooms=0), then=Value("Студия")),
            When(Q(rooms=1), then=Value("1")),
            When(Q(rooms=2), then=Value("2")),
            When(Q(rooms=3), then=Value("3")),
            When(Q(rooms__gte=4), then=Value("4+")),
            output_field=CharField(),
        )

        return self.annotate(rooms_type=rooms_type)

    def annotate_completed(self) -> PropertyQuerySet:
        current_date = now().date()

        completed = Case(
            When(
                Q(building__building_state__in=[Building.STATE_READY, Building.STATE_HAND_OVER])
                | Q(building__built_year__lt=current_date.year)
                | (
                    Q(building__built_year=current_date.year)
                    & Q(building__ready_quarter__lt=(current_date.month - 1 // 3) + 1)
                ),
                then=True,
            ),
            default=False,
            output_field=BooleanField(),
        )

        return self.annotate(completed=completed)

    def annotate_infra(self) -> PropertyQuerySet:
        from infras.models import MainInfra, MainInfraContent

        infra = Subquery(
            MainInfra.objects.filter(project__property=OuterRef("pk"))
            .order_by("id")
            .values("name")[:1]
        )

        infra_text = Subquery(
            MainInfra.objects.filter(project__property=OuterRef("pk"))
            .order_by("id")
            .annotate(
                infra_text=Subquery(
                    MainInfraContent.objects.filter(main_infra=OuterRef("pk"))
                    .order_by("id")
                    .values("value")[:1]
                )
            )
            .values("infra_text")[:1]
        )

        return self.annotate(infra=infra, infra_text=infra_text)

    def annotate_building_total_floor(self) -> PropertyQuerySet:
        from buildings.models import Section

        section_total_floor = Subquery(
            Section.objects.filter(id=OuterRef("section"))
            .annotate_total_floor()
            .values("total_floor")[:1]
        )

        return self.annotate(building_total_floor=section_total_floor)

    def annotate_min_mortgage(self, deposit: float = 20.0) -> PropertyQuerySet:
        from mortgage.models import Offer

        deposit = int(deposit)
        min_mortgage = (
            Offer.objects.filter(
                is_active=True, projects=OuterRef("project"), type=OuterRef("mortgage_type")
            )
            .annotate(
                max_term=Greatest(Upper("term"), Lower("term")),
                max_deposit=Greatest(Upper("deposit"), Lower("deposit")),
                max_amount=Greatest(Upper("amount"), Lower("amount")),
                min_rate=Least(Lower("rate"), Upper("rate")),
            )
            .filter(max_amount__gte=OuterRef("price") - OuterRef("price") * 100 / deposit)
            .annotate_payment(OuterRef("price"), deposit, 25)
            .order_by("payment")
        )

        return self.annotate(
            min_mortgage=Subquery(min_mortgage.values("payment")[:1]),
            min_rate=Subquery(min_mortgage.values("min_rate")[:1]),
        )

    def annotate_min_furnish_mortgage(self, deposit: float = 20.0) -> PropertyQuerySet:
        from mortgage.models import Offer

        deposit = int(deposit)
        min_mortgage = (
            Offer.objects.filter(
                is_active=True, projects=OuterRef("project"), type=OuterRef("mortgage_type")
            )
                .annotate(
                max_term=Greatest(Upper("term"), Lower("term")),
                max_deposit=Greatest(Upper("deposit"), Lower("deposit")),
                max_amount=Greatest(Upper("amount"), Lower("amount")),
                min_rate=Least(Lower("rate"), Upper("rate")),
            )
                .filter(max_amount__gte=OuterRef("furnish_price") - OuterRef("furnish_price") * 100 / deposit)
                .annotate_payment(OuterRef("furnish_price"), deposit, 25)
                .order_by("payment")
        )

        return self.annotate(
            min_furnish_mortgage=Subquery(min_mortgage.values("payment")[:1]),
            min_furnish_rate=Subquery(min_mortgage.values("min_rate")[:1]),
        )

    def annotate_min_furnish_comfort_mortgage(self, deposit: float = 20.0) -> PropertyQuerySet:
        from mortgage.models import Offer

        deposit = int(deposit)
        min_mortgage = (
            Offer.objects.filter(
                is_active=True, projects=OuterRef("project"), type=OuterRef("mortgage_type")
            )
                .annotate(
                max_term=Greatest(Upper("term"), Lower("term")),
                max_deposit=Greatest(Upper("deposit"), Lower("deposit")),
                max_amount=Greatest(Upper("amount"), Lower("amount")),
                min_rate=Least(Lower("rate"), Upper("rate")),
            )
                .filter(max_amount__gte=OuterRef("furnish_price_comfort") -
                                        OuterRef("furnish_price_comfort") * 100 / deposit)
                .annotate_payment(OuterRef("furnish_price_comfort"), deposit, 25)
                .order_by("payment")
        )

        return self.annotate(
            min_furnish_comfort_mortgage=Subquery(min_mortgage.values("payment")[:1]),
            min_furnish_comfort_rate=Subquery(min_mortgage.values("min_rate")[:1]),
        )

    def annotate_min_furnish_business_mortgage(self, deposit: float = 20.0) -> PropertyQuerySet:
        from mortgage.models import Offer

        deposit = int(deposit)
        min_mortgage = (
            Offer.objects.filter(
                is_active=True, projects=OuterRef("project"), type=OuterRef("mortgage_type")
            )
                .annotate(
                max_term=Greatest(Upper("term"), Lower("term")),
                max_deposit=Greatest(Upper("deposit"), Lower("deposit")),
                max_amount=Greatest(Upper("amount"), Lower("amount")),
                min_rate=Least(Lower("rate"), Upper("rate")),
            )
                .filter(max_amount__gte=OuterRef("furnish_price_business") -
                                        OuterRef("furnish_price_business") * 100 / deposit)
                .annotate_payment(OuterRef("furnish_price_business"), deposit, 25)
                .order_by("payment")
        )

        return self.annotate(
            min_furnish_business_mortgage=Subquery(min_mortgage.values("payment")[:1]),
            min_furnish_business_rate=Subquery(min_mortgage.values("min_rate")[:1]),
        )

    def annotate_min_furnish_kitchen_mortgage(self, deposit: float = 20.0) -> PropertyQuerySet:
        from mortgage.models import Offer

        deposit = int(deposit)
        min_mortgage = (
            Offer.objects.filter(
                is_active=True, projects=OuterRef("project"), type=OuterRef("mortgage_type")
            )
                .annotate(
                max_term=Greatest(Upper("term"), Lower("term")),
                max_deposit=Greatest(Upper("deposit"), Lower("deposit")),
                max_amount=Greatest(Upper("amount"), Lower("amount")),
                min_rate=Least(Lower("rate"), Upper("rate")),
            )
                .filter(max_amount__gte=OuterRef("furnish_kitchen_price") -
                                        OuterRef("furnish_kitchen_price") * 100 / deposit)
                .annotate_payment(OuterRef("furnish_kitchen_price"), deposit, 25)
                .order_by("payment")
        )

        return self.annotate(
            min_furnish_kitchen_mortgage=Subquery(min_mortgage.values("payment")[:1]),
            min_furnish_kitchen_rate=Subquery(min_mortgage.values("min_rate")[:1]),
        )

    def annotate_min_furnish_furniture_mortgage(self, deposit: float = 20.0) -> PropertyQuerySet:
        from mortgage.models import Offer

        deposit = int(deposit)
        min_mortgage = (
            Offer.objects.filter(
                is_active=True, projects=OuterRef("project"), type=OuterRef("mortgage_type")
            )
                .annotate(
                max_term=Greatest(Upper("term"), Lower("term")),
                max_deposit=Greatest(Upper("deposit"), Lower("deposit")),
                max_amount=Greatest(Upper("amount"), Lower("amount")),
                min_rate=Least(Lower("rate"), Upper("rate")),
            )
                .filter(max_amount__gte=OuterRef("furnish_furniture_price") -
                                        OuterRef("furnish_furniture_price") * 100 / deposit)
                .annotate_payment(OuterRef("furnish_furniture_price"), deposit, 25)
                .order_by("payment")
        )

        return self.annotate(
            min_furnish_furniture_mortgage=Subquery(min_mortgage.values("payment")[:1]),
            min_furnish_furniture_rate=Subquery(min_mortgage.values("min_rate")[:1]),
        )

    def annotate_min_furnish_kitchen_furniture_mortgage(self, deposit: float = 20.0) -> PropertyQuerySet:
        from mortgage.models import Offer

        deposit = int(deposit)
        min_mortgage = (
            Offer.objects.filter(
                is_active=True, projects=OuterRef("project"), type=OuterRef("mortgage_type")
            )
                .annotate(
                max_term=Greatest(Upper("term"), Lower("term")),
                max_deposit=Greatest(Upper("deposit"), Lower("deposit")),
                max_amount=Greatest(Upper("amount"), Lower("amount")),
                min_rate=Least(Lower("rate"), Upper("rate")),
            )
                .filter(max_amount__gte=OuterRef("furnish_kitchen_furniture_price") -
                                        OuterRef("furnish_kitchen_furniture_price") * 100 / deposit)
                .annotate_payment(OuterRef("furnish_kitchen_furniture_price"), deposit, 25)
                .order_by("payment")
        )

        return self.annotate(
            min_furnish_kitchen_furniture_mortgage=Subquery(min_mortgage.values("payment")[:1]),
            min_furnish_kitchen_furniture_rate=Subquery(min_mortgage.values("min_rate")[:1]),
        )

    def annotate_has_auction(self) -> PropertyQuerySet:

        auction_qs = (
            Auction.objects.filter_active().not_finished().filter(property_object_id=OuterRef("id"))
        )

        return self.annotate(has_auction=Exists(auction_qs))

    def annotate_building_specs(self) -> PropertyQuerySet:

        label = Concat(
            F("building__name_display"),
            Value(" ("),
            F("building__ready_quarter"),
            Value(" кв. "),
            F("building__built_year"),
            Value(")"),
            output_field=CharField(),
        )
        value = F("building_id")

        return self.annotate(label=label, value=value)

    def annotate_booking_days(self) -> PropertyQuerySet:
        booking_days = Subquery(
            Building.objects.filter(property=OuterRef("pk")).values("booking_period")[:1]
        )
        return self.annotate(booking_days=booking_days)

    def annotate_has_balcony_or_loggia(self) -> PropertyQuerySet:

        has_balcony_or_loggia = Case(
            When(
                Q(balconies_count__gt=0) | Q(loggias_count__gt=0) | Q(lounge_balcony=True),
                then=True,
            ),
            default=False,
            output_field=BooleanField(),
        )

        return self.annotate(has_balcony_or_loggia=has_balcony_or_loggia)

    def annotate_price_with_offer(self):
        from .models import SpecialOffer

        special_offers = (
            SpecialOffer.objects.filter(
                properties=OuterRef("pk"), is_active=True, discount_value__gt=0
            )
            .annotate(
                calculate_price=Case(
                    When(
                        discount_unit="PERCENT",
                        then=OuterRef("original_price")
                        - OuterRef("original_price") / Value(100) * F("discount_value"),
                    ),
                    default=OuterRef("original_price") - F("discount_value"),
                    output_field=IntegerField(),
                )
            )
            .order_by("calculate_price")
            .values("calculate_price")
        )
        return self.annotate(
            price_with_offer_a=Subquery(special_offers[:1]),
            price_with_offer=Case(
                When(price_with_offer_a__isnull=False, then=F("price_with_offer_a")),
                default=F("original_price"),
                output_field=IntegerField(),
            ),
        )


class LayoutQuerySet(PropertyAndLayoutQuerySet):
    def window_view_annotated(self):
        from .models import Property

        window_view = Subquery(
            Property.objects.filter(layout=OuterRef("pk"))
            .values("window_view_id")
            .order_by(F("window_view").asc(nulls_last=True))[:1]
        )
        return self.annotate(window_view_a=window_view)

    def annotate_max_discount(self):
        from .models import Property

        max_discount = Subquery(
            Property.objects.filter(layout=OuterRef("pk"), status=PropertyStatus.FREE)
            .annotate(discount=F("original_price") - F("price"), max_discount=Max(F("discount")))
            .values("max_discount")
            .order_by(F("max_discount").desc())[:1]
        )
        return self.annotate(max_discount_a=max_discount)

    def plan_hover_annotated(self):
        from .models import Property

        plan_hover = Subquery(
            Property.objects.filter(layout=OuterRef("pk"), floor=OuterRef("floor"))
            .values("plan_hover")
            .order_by(F("plan_hover").asc(nulls_last=True))[:1]
        )
        return self.annotate(plan_hover_a=plan_hover)

    def admin_annotated(self):
        return self.prefetch_related("property_set").select_related(
            "window_view", "floor", "building", "project"
        )

    def annotate_has_special_offers(self):

        from .models import SpecialOffer

        special_offers = SpecialOffer.objects.filter(
            is_active=True,
            properties__article=OuterRef("name"),
            properties__status=PropertyStatus.FREE,
        )
        return self.annotate(has_special_offers=Exists(special_offers))

    def annotate_has_badge(self):

        from .models import SpecialOffer
        has_badge = SpecialOffer.objects.filter(
            is_active=True,
            badge_label=FeatureType.INSTALLMENT.label,
            properties__article=OuterRef("name"),
            properties__status=PropertyStatus.FREE,
        )
        return self.annotate(has_badge=Exists(has_badge))

    def annotate_type(self):
        from .models import Property

        type_ = Subquery(
            Property.objects.filter(layout=OuterRef("pk"))
            .values("type")
            .order_by(F("type").asc(nulls_last=True))[:1]
        )

        return self.annotate(type_a=type_)

    def annotate_min_price(self):
        from .models import Property

        min_price = Subquery(
            Property.objects.filter(
                layout=OuterRef("pk"),
                type__in=[PropertyType.FLAT, PropertyType.COMMERCIAL_APARTMENT],
                status=PropertyStatus.FREE,
                price__gt=0,
            )
            .values("price")
            .order_by(F("price"))[:1]
        )
        return self.annotate(min_price_a=min_price)

    def annotate_min_mortgage(self) -> PropertyQuerySet:
        from mortgage.models import Offer

        min_mortgage = Subquery(
            Offer.objects.filter(
                is_active=True, projects=OuterRef("project"), type=OuterRef("mortgage_type")
            )
            .annotate(
                max_term=Greatest(Upper("term"), Lower("term")),
                max_deposit=Greatest(Upper("deposit"), Lower("deposit")),
                max_amount=Greatest(Upper("amount"), Lower("amount")),
            )
            .filter(max_amount__gte=OuterRef("min_price") - OuterRef("min_price") * 100 / 20)
            .annotate_payment(OuterRef("min_price"), 20, 25)
            .order_by("payment")
            .values("payment")[:1]
        )

        return self.annotate(min_mortgage_a=min_mortgage)

    def annotate_min_rate(self) -> LayoutQuerySet:

        from mortgage.models import Offer

        min_rate = Subquery(
            Offer.objects.filter(
                is_active=True, projects=OuterRef("project"), type=OuterRef("mortgage_type")
            )
            .annotate(min_rate=Least(Upper("rate"), Lower("rate")))
            .order_by("min_rate")
            .values("min_rate")[:1]
        )

        return self.annotate(min_rate_a=min_rate)

    def annotate_property_stats(self, flat_qs = None, params: dict = None):
        from .models import Property

        partition_by = {"partition_by": F("pk")}
        price = Window(
            expression=FirstValue(
                "property__price", filter=Q(property__status=PropertyStatus.FREE)
            ),
            order_by=F("property__price").asc(),
            **partition_by,
        )
        original_price = Window(
            expression=FirstValue(
                "property__original_price", filter=Q(property__status=PropertyStatus.FREE)
            ),
            order_by=F("property__price").asc(),
            **partition_by,
        )
        if flat_qs:
            flat_subq = flat_qs.filter(layout=OuterRef("pk"))
        else:
            flat_subq = Property.objects.filter_active().filter(layout=OuterRef("pk"))
        if params and isinstance(params, dict):
            flat_subq = flat_subq.filter(**params)
        first_flat_id = Subquery(flat_subq.order_by("pk").values("id")[:1])
        return self.annotate(price=price, original_price=original_price, first_flat_id=first_flat_id)

    def annotate_dynamic_flat_count(self, property_set: QuerySet):
        partition_by = {"partition_by": F("pk")}
        flat_count = Window(
            expression=Count("property", filter=Q(property__in=property_set)),
            **partition_by
        )
        return self.annotate(dynamic_flat_count=flat_count)

    def annotate_property_stats_dynamic(self, property_set: QuerySet):
        """Динамическое аннотирование свойств планировок."""
        partition_by = {"partition_by": F("pk")}
        min_floor = Window(
            expression=Min("property__floor__number", filter=Q(property__in=property_set)),
            **partition_by
        )
        max_floor = Window(
            expression=Max("property__floor__number", filter=Q(property__in=property_set)),
            **partition_by
        )
        return self.annotate(
            min_floor_a=min_floor,
            max_floor_a = max_floor
        )


    def annotate_property_stats_static(self):
        from .models import Property

        active_property = Property.objects.filter_active()
        filter_property = active_property.filter(layout=OuterRef("pk")).select_related("floor")
        plan = Subquery(
            filter_property.filter(plan__isnull=False)
            .exclude(plan="")
            .order_by("plan")
            .values("plan")[:1]
        )
        planoplan = Subquery(
            filter_property.filter(planoplan__isnull=False)
            .exclude(planoplan="")
            .order_by("planoplan")
            .values("planoplan")[:1]
        )

        area = Subquery(
            filter_property.filter(area__isnull=False).order_by("area").values("area")[:1]
        )
        min_floor = Subquery(filter_property.order_by("floor__number").values("floor__number")[:1])
        max_floor = Subquery(filter_property.order_by("-floor__number").values("floor__number")[:1])
        rooms = Subquery(
            filter_property.filter(rooms__isnull=False).order_by("rooms").values("rooms")[:1]
        )
        flat_count = Subquery(
            filter_property.annotate(
                count=Count(
                    "layout__property",
                    filter=Q(layout__property__id__in=active_property.values_list("id", flat=True)),
                )
            ).values("count")[:1]
        )
        has_view = Subquery(filter_property.order_by("-has_view").values("has_view")[:1])
        has_parking = Subquery(filter_property.order_by("-has_parking").values("has_parking")[:1])
        has_action_parking = Subquery(
            filter_property.order_by("-has_action_parking").values("has_action_parking")[:1]
        )
        has_terrace = Subquery(filter_property.order_by("-has_terrace").values("has_terrace")[:1])
        has_high_ceiling = Subquery(
            filter_property.order_by("-has_high_ceiling").values("has_high_ceiling")[:1]
        )
        has_two_sides_windows = Subquery(
            filter_property.order_by("-has_two_sides_windows").values("has_two_sides_windows")[:1]
        )
        has_panoramic_windows = Subquery(
            filter_property.order_by("-has_panoramic_windows").values("has_panoramic_windows")[:1]
        )
        is_duplex = Subquery(filter_property.order_by("-is_duplex").values("is_duplex")[:1])
        installment = Subquery(filter_property.order_by("-installment").values("installment")[:1])
        facing = Subquery(
            filter_property.filter(facing__isnull=False).order_by("-facing").values("facing")[:1]
        )
        stores_count = Subquery(
            filter_property.filter(stores_count__gte=1).order_by("-stores_count").values("stores_count")[:1])
        frontage = Subquery(filter_property.order_by("-frontage").values("frontage")[:1])
        preferential_mortgage4 = Subquery(
            filter_property.order_by("-preferential_mortgage4").values("preferential_mortgage4")[:1]
        )
        maternal_capital = Subquery(
            filter_property.order_by("-maternal_capital").values("maternal_capital")[:1]
        )
        hypo_popular = Subquery(
            filter_property.order_by("-hypo_popular").values("hypo_popular")[:1]
        )
        filter_property = filter_property.order_by("price")
        first_flat_id = Subquery(filter_property.values("id")[:1])
        floor_plan = Subquery(
            filter_property.filter(floor__plan__isnull=False)
            .exclude(floor__plan="")
            .values("floor__plan")[:1]
        )
        floor_plan_height = Subquery(
            filter_property.filter(floor__plan_height__isnull=False).values("floor__plan_height")[
                :1
            ]
        )

        floor_plan_width = Subquery(
            filter_property.filter(floor__plan_width__isnull=False).values("floor__plan_width")[:1]
        )
        design_gift = Subquery(filter_property.order_by("-design_gift").values("design_gift")[:1])
        flat_sold = Subquery(
            filter_property.annotate(
                count=Count(
                    "layout__property", filter=Q(layout__property__status=PropertyStatus.SOLD)
                )
            ).values("count")[:1]
        )
        return self.annotate(
            plan_a=plan,
            planoplan_a=planoplan,
            area_a=area,
            min_floor_a=min_floor,
            max_floor_a=max_floor,
            flat_count_a=flat_count,
            rooms_a=rooms,
            has_view_a=has_view,
            has_parking_a=has_parking,
            stores_count_a=stores_count,
            has_action_parking_a=has_action_parking,
            has_terrace_a=has_terrace,
            has_high_ceiling_a=has_high_ceiling,
            has_two_sides_windows_a=has_two_sides_windows,
            has_panoramic_windows_a=has_panoramic_windows,
            is_duplex_a=is_duplex,
            installment_a=installment,
            facing_a=facing,
            frontage_a=frontage,
            first_flat_id_a=first_flat_id,
            preferential_mortgage4_a=preferential_mortgage4,
            maternal_capital_a=maternal_capital,
            floor_plan_a=floor_plan,
            floor_plan_width_a=floor_plan_width,
            floor_plan_height_a=floor_plan_height,
            hypo_popular_a=hypo_popular,
            design_gift_a=design_gift,
            flat_sold_a=flat_sold,
        )

    def annotate_most_expensive(self):
        max_price_id = self.order_by("price").values_list("id", flat=True).last()
        return self.annotate(
            most_expensive=Case(
                When(id=Value(max_price_id), then=Value(0)),
                When(price__lt=F("original_price"), then=Value(1)),
                default=Value(2),
                output_field=IntegerField(),
            )
        )


class SpecialOfferQuerySet(ActiveQuerySet):
    def annotate_activity(self):
        now_ = now()
        is_active = Case(
            When(Q(start_date__lt=now_, finish_date__gt=now_), then=True),
            When(
                Q(finish_date__lt=now_) & Q(start_date__lt=now_) | Q(start_date__gt=now_),
                then=False,
            ),
            output_field=BooleanField(),
        )
        return self.annotate(is_active_a=is_active)


class FeatureQuerySet(QuerySet):
    def for_filter(self, property_kind, request) -> FeatureQuerySet:
        from django.conf import settings
        filter_ = Q(filter_show=True, property_kind__contains=[property_kind])
        if not settings.TESTING:
            if hasattr(request, "site") and hasattr(request.site, "city"):
                filter_ &= Q(cities=request.site.city)

        return self.filter(filter_).distinct()
