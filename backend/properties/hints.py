from django.db.models import Prefetch
from graphene_django_optimizer import query
from .models import Property, SpecialOffer, TrafficMap
from .constants import PropertyType


def layout_resolve_flat_set_hint(info) -> Prefetch:
    queryset = query(
        Property.objects.filter_active().filter(
            type__in=[PropertyType.FLAT, PropertyType.COMMERCIAL_APARTMENT]
        ),
        info,
    )
    return Prefetch("property_set", queryset, to_attr="prefetched_flat_set")


def flat_resolve_special_offer_set_hint(info) -> Prefetch:
    queryset = query(SpecialOffer.objects.filter(is_active=True), info)
    return Prefetch("specialoffer_set", queryset, to_attr="prefetched_specialoffer_set")

def trafficmap_set_hint(info) -> Prefetch:
    queryset = query(TrafficMap.objects.all(), info)
    return Prefetch("trafficmap_set", queryset, to_attr="prefetched_trafficmap_set")