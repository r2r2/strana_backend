from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ReadOnlyModelViewSet

from buildings.models import Building, GroupSection, Section, Floor
from ..filters import BuildingFilter
from ..serializers.genplan import BuildingSectionGroupGenplanSerializer


class BuildingViewSet(ReadOnlyModelViewSet):
    queryset = (
        Building.objects.filter_active()
        .annotate_total_floor()
        .annotate_flats_count()
        .annotate_parking_count()
        .annotate_commercial_count()
        .select_related("project")
        .prefetch_related(
            Prefetch(
                "groupsection_set",
                GroupSection.objects.all(),
            ),
            Prefetch(
                "section_set",
                Section.objects.annotate_total_floor()
                .annotate_flats_count()
                .prefetch_related(
                    Prefetch(
                        "floor_set",
                        Floor.objects.all(),
                    )
                ),
            ),
        )
    )
    serializer_class = BuildingSectionGroupGenplanSerializer
    filterset_class = BuildingFilter
    filter_backends = (DjangoFilterBackend,)

    @method_decorator(cache_page(60 * 5))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
