from django.db.models import Prefetch
from graphene_django_optimizer import query

from buildings.models import Building
from properties.models import Property, TrafficMap


def project_resolve_building_set_hint(info) -> Prefetch:
    queryset = query(Building.objects.filter_active(), info)
    return Prefetch("building_set", queryset, to_attr="prefetched_buildings")


def project_resolve_traffic_map_hint(info) -> Prefetch:
    queryset = query(TrafficMap.objects.filter_active(), info)
    return Prefetch("trafficmap_set", queryset, to_attr="prefetched_trafficmaps")

# def project_resolve_commercial_price_range(info) -> Prefetch:
#     queryset = query(Property.objects.)