from django.db.models import Prefetch
from graphene_django_optimizer import query

from auction.models import Auction
from properties.constants import PropertyType, PropertyStatus
from properties.models import Property
from .models import Section, Floor, GroupSection, Building, FloorExitPlan


def floor_resolve_flat_set_hint(info) -> Prefetch:
    queryset = query(
        Property.objects.filter(
            type__in=[PropertyType.FLAT, PropertyType.COMMERCIAL_APARTMENT],
            status=PropertyStatus.FREE,
        ),
        info,
    )
    return Prefetch("property_set", queryset, to_attr="prefetched_flats")


def floor_resolve_commercial_set_hint(info) -> Prefetch:
    queryset = query(Property.objects.filter(type=PropertyType.COMMERCIAL), info)
    return Prefetch("property_set", queryset, to_attr="prefetched_commercial")


def section_resolve_floor_set_hint(info) -> Prefetch:
    queryset = query(
        Floor.objects.annotate_flats_count().annotate_commercial_count().annotate_parking_count().annotate_pantry_count(),
        info,
    )
    return Prefetch("floor_set", queryset, to_attr="prefetched_floors")


def group_section_resolve_section_set_hint(info) -> Prefetch:
    queryset = query(Section.objects.annotate_total_floor().annotate_flats_count(), info)
    return Prefetch("section_set", queryset, to_attr="prefetched_section")


def building_resolve_section_set_hint(info) -> Prefetch:
    queryset = query(Section.objects.annotate_total_floor(), info)
    return Prefetch("section_set", queryset, to_attr="prefetched_sections")


def building_resolve_residential_set_hint(info) -> Prefetch:
    queryset = query(Building.objects.annotate_flats_count().annotate_commercial_count(), info)
    return Prefetch("residential_set", queryset, to_attr="prefetched_residential")


def building_resolve_groupsection_set_hint(info) -> Prefetch:
    queryset = query(GroupSection.objects.all(), info)
    return Prefetch("groupsection_set", queryset, to_attr="prefetched_groupsections")


def commercial_space_resolve_auction_hint(info) -> Prefetch:
    queryset = query(
        Auction.objects.filter_active().annotate_is_current().annotate_current_price(), info
    )
    return Prefetch("auction_set", queryset, to_attr="prefetched_auction_set")


def floor_exit_plan_resolve_set_hint(info) -> Prefetch:
    queryset = query(FloorExitPlan.objects.all(), info)
    return Prefetch("floorexitplan_set", queryset, to_attr="prefetched_floor_exit_plan")
