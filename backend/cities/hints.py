from django.db.models import Prefetch
from graphene_django_optimizer import query

from projects.models import Project

from .models import City, ProjectSlide


def city_resolve_project_slides_hint(info) -> Prefetch:
    queryset = query(ProjectSlide.objects.filter_active(), info)
    return Prefetch("project_slides", queryset, to_attr="prefetched_project_slides")


def city_resolve_hint(info) -> Prefetch:
    queryset = query(City.objects.annotate_is_commercial().annotate_has_active_projects(), info)
    return Prefetch("city", queryset, to_attr="prefetched_cities")


def city_resolve_project_set_hint(info) -> Prefetch:
    from projects.schema import ProjectType
    queryset = query(
        Project.objects.filter_active().annotate_flats_prices()
                .annotate_min_rooms_prices()
                .annotate_parking_pantry_count()
                .annotate_flats_count()
                .annotate_parking_pantry_area()
                .annotate_commercial_prices().annotate_commercial_area().annotate_commercial_count()
                .annotate_parking_pantry_price().annotate_min_prop_price(), info
    )
    # queryset = query(
    #     Project.objects.filter_active().annotate_flats_count().annotate_commercial_count(), info
    # )
    return Prefetch("project_set", queryset, to_attr="prefetched_projects")
