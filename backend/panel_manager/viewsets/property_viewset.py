from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from buildings.models import Building
from properties.constants import PropertyType
from properties.models import Property, Furnish, Layout
from ..filters import FlatFilter, LayoutFilter
from ..models import Meeting
from ..serializers import FlatSerializer, BookingSerializer, LayoutSerializer, FlatListSerializer


class FlatPagination(LimitOffsetPagination):
    default_limit = 10


class PanelManagerFlatViewSet(ReadOnlyModelViewSet):
    pagination_class = FlatPagination
    filterset_class = FlatFilter
    filter_backends = (DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.action == "booking":
            return BookingSerializer
        if self.action == "layouts":
            return LayoutSerializer
        if self.action == "list":
            return FlatListSerializer
        return FlatSerializer

    def get_queryset(self):
        return (
            Property.objects.filter(type__in=[PropertyType.FLAT, PropertyType.COMMERCIAL_APARTMENT])
            .select_related(
                "floor__section", "project", "section__building", "window_view__type__building"
            )
            .prefetch_related(
                "window_view__windowviewangle_set",
                "project__projectfeature_set",
                "mini_plan_point__miniplanpointangle_set",
                Prefetch(
                    "furnish_set",
                    Furnish.objects.prefetch_related(
                        "image_set__point_set", "furnishadvantage_set", "jobdescription_set"
                    ),
                ),
                Prefetch(
                    "building",
                    Building.objects.prefetch_related(
                        Prefetch(
                            "furnish_set",
                            Furnish.objects.prefetch_related(
                                "image_set__point_set", "furnishadvantage_set", "jobdescription_set"
                            ),
                        )
                    ),
                ),
            )
            .filter_active()
            .annotate_has_discount()
            .annotate_rooms_type()
            .annotate_is_favorite(self.request.favorite.keys)
            .annotate_completed()
            .annotate_infra()
            .annotate_first_payment()
            .annotate_building_total_floor()
            .annotate_mortgage_type()
            .annotate_min_mortgage()
            .order_plan()
            .annotate_booking_days()
            .annotate_has_balcony_or_loggia()
        )

    @action(detail=False, methods=("GET",))
    def specs(self, request):
        queryset = self.get_queryset()
        filter = self.filterset_class(request.GET, queryset, request=request)
        return Response(filter.specs())

    @action(detail=False, methods=("GET",))
    def facets(self, request):
        queryset = self.get_queryset()
        filter = self.filterset_class(request.GET, queryset, request=request)
        return Response(filter.facets())

    @action(detail=True, methods=("POST",))
    def booking(self, request, pk, *args, **kwargs):
        """Бронирование на помещения на панели менеджера"""
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        m = Meeting.objects.get(id=str(serializer.data["meeting"]))
        m.booked_property = instance
        # m.meeting_end_type = MeetingEndTypeChoices.BOOKING
        m.save()
        return Response(status=200)

    @action(detail=False, methods=("GET",))
    def layouts(self, request, *args, **kwargs):
        """Вывод по планировочным решениям"""

        queryset = self.filter_queryset(self.get_queryset())
        queryset = (
            Layout.objects.filter(property__in=queryset.values_list("pk", flat=True))
            .prefetch_related(
                "building",
                "project",
                "floor",
                "window_view__windowviewangle_set",
                "window_view__type",
            )
            .annotate_property_stats(queryset).annotate_property_stats_dynamic(queryset)
            .annotate_dynamic_flat_count(queryset)
            .distinct()
        )
        queryset = LayoutFilter(self.request.GET, queryset, request=self.request).qs

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
