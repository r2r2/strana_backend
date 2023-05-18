from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ReadOnlyModelViewSet

from buildings.models import Floor
from properties.models import Property
from ..filters import FloorFilter
from ..serializers.genplan import FloorGenplanSerializer, FloorSectionSerializer


class FloorViewSet(ReadOnlyModelViewSet):
    queryset = (
        Floor.objects.all()
        .annotate_flats_min_price()
        .annotate_flats_count()
        .annotate_commercial_count()
        .annotate_parking_count()
        .prefetch_related(
            Prefetch(
                "property_set",
                Property.objects.all()
                .select_related("floor", "project", "building", "section", "window_view__type")
                .filter_active()
                .annotate_has_discount()
                .annotate_rooms_type()
                .annotate_completed()
                .annotate_infra()
                .annotate_first_payment()
                .annotate_building_total_floor()
                .annotate_mortgage_type()
                .annotate_min_mortgage()
                #.annotate_bank_logo()
                .order_plan()
                .annotate_booking_days(),
            )
        )
    )
    filterset_class = FloorFilter
    filter_backends = (DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.action == "list":
            return FloorSectionSerializer
        return FloorGenplanSerializer
