from django.db.models import F, OuterRef, Q, Subquery
from django.db.models.functions import Greatest, Least, Lower, Upper

from mortgage.constants import MortgageType
from mortgage.models import Offer
from projects.models import Project

from properties.models import Property
from properties.constants import COMMERCIAL_TYPES, FLAT_TYPES, PropertyStatus, PropertyType


def calculate_project_min_prop_price() -> None:
    room_params = {
        f"flats_{rooms_count}_min_price":
            Subquery(Property.objects.filter(
                type__in=FLAT_TYPES,
                rooms=rooms_count,
                status=PropertyStatus.FREE,
                project=OuterRef("pk"),
                building__is_active=True,
            )
            .values("price")
            .order_by("price")[:1])
        for rooms_count in range(5)
    }
    prop_params = {
        "min_flat_price": Subquery(Property.objects.filter(
                project=OuterRef("pk"),
                type__in=FLAT_TYPES,
                status=PropertyStatus.FREE,
                building__is_active=True,
            )
            .order_by("price")
            .values("price")[:1]),
        "min_commercial_prop_price": Subquery(Property.objects.filter(
                project=OuterRef("pk"), type__in=COMMERCIAL_TYPES, status=PropertyStatus.FREE
            )
            .order_by("price")
            .values("price")[:1]),
        "min_commercial_tenant_price": Subquery(Property.objects.filter(
                project=OuterRef("pk"),
                type__in=COMMERCIAL_TYPES,
                status=PropertyStatus.FREE,
                has_tenant=True,
            )
            .order_by("price")
            .values("price")[:1]),
        "min_commercial_business_price": Subquery(Property.objects.filter(
                project=OuterRef("pk"),
                type__in=COMMERCIAL_TYPES,
                status=PropertyStatus.FREE,
                for_business=True,
            )
            .order_by("price")
            .values("price")[:1])
    }
    Project.objects.update(**room_params)
    Project.objects.update(**prop_params)


def calculate_project_prop_area_range() -> None:
    prop_q = Q(project=OuterRef("pk"), status=PropertyStatus.FREE, building__is_active=True)
    prop_area_data = {
        "min_flat_area": Subquery(Property.objects.filter(prop_q, type__in=FLAT_TYPES).order_by("area").values("area")[:1]),
        "max_flat_area": Subquery(Property.objects.filter(prop_q, type__in=FLAT_TYPES).order_by("-area").values("area")[:1])
    }
    commercial_data = {
        "min_commercial_prop_area": Subquery(
            Property.objects.filter(prop_q, type__in=COMMERCIAL_TYPES).order_by("area").values("area")[:1]),
        "max_commercial_prop_area": Subquery(
            Property.objects.filter(prop_q, type__in=COMMERCIAL_TYPES).order_by("-area").values("area")[:1])
    }
    projects = Project.objects.all()
    projects.update(**prop_area_data)
    projects.exclude(dont_commercial_prop_update=True).update(**commercial_data)


def calculate_project_min_rooms_prices() -> None:
    room_params = {
        f"flats_{rooms_count}_min_price":
            Subquery(Property.objects.filter(
                type__in=FLAT_TYPES,
                rooms=rooms_count,
                status=PropertyStatus.FREE,
                project=OuterRef("pk"),
                building__is_active=True,
            )
            .values("price")
            .order_by("price")[:1])
        for rooms_count in range(5)
    }
    projects = Project.objects.all()
    projects.update(**room_params)


def calculate_project_min_rate_offers() -> None:
    Project.objects.update(
        min_rate_offers=Subquery(
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
        ))


def calculate_project_min_mortgage() -> None:
    mortgage_props = {
        "min_flat_mortgage": Subquery(
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
        ),
        "min_commercial_mortgage": Subquery(
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
    }
    Project.objects.update(**mortgage_props)


def calculate_project_bank_logo() -> None:
    projects = Project.objects.annotate_bank_logo()
    projects.update(bank_logo_1=F("bank_logo_1_a"), bank_logo_2=F("bank_logo_2_a"))


def calculate_project_label_with_completion() -> None:
    projects = Project.objects.filter(auto_update_label=True).annotate_label_with_completion()
    projects.update(label_with_completion=F("label_with_completion_a"))


def update_count_pantry_parking() -> None:
    projects = Project.objects.all()
    for project in projects:
        parking_count = Property.objects.filter(
            project=project,
            type=PropertyType.PARKING

        ).count()
        pantry_count = Property.objects.filter(
            project=project,
            type=PropertyType.PANTRY
        ).count()

        project.business_parking_count = parking_count
        project.business_pantry_count = pantry_count

    Project.objects.bulk_update(projects, ['business_parking_count', 'business_pantry_count'])
