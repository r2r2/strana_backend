from django.db.models import Prefetch
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ReadOnlyModelViewSet

from buildings.models import Section, Floor
from ..filters import SectionFilter
from ..serializers.genplan import SectionGenplanSerializer


class SectionViewSet(ReadOnlyModelViewSet):
    queryset = (
        Section.objects.all()
        .annotate_total_floor()
        .annotate_flats_count()
        .select_related("building")
        .prefetch_related(
            Prefetch(
                "floor_set", Floor.objects.all().annotate_flats_count().select_related("section")
            )
        )
    )
    serializer_class = SectionGenplanSerializer
    filterset_class = SectionFilter
    filter_backends = (DjangoFilterBackend,)

    @method_decorator(cache_page(60 * 20))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
