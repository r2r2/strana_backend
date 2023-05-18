from typing import Type

from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, BasePermission
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import ReadOnlyModelViewSet

from buildings.models import Building
from projects.models import Project
from projects.querysets import ProjectQuerySet
from properties.models import (Furnish, FurnishFurniture, FurnishImage,
                               FurnishKitchen)

from ..filters import ProjectFilter
from ..serializers import ProjectListSerializer, ProjectRetrieveSerializer
from ..serializers.genplan import ProjectGenplanSerializer


class PanelManagerProjectViewSet(ReadOnlyModelViewSet):
    """
    Проекты
    """

    filterset_class: Type[FilterSet] = ProjectFilter
    permission_classes: tuple[Type[BasePermission]] = (AllowAny,)
    lookup_field: str = "slug"
    lookup_url_kwarg: str = "slug"
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self) -> ProjectQuerySet:
        queryset: ProjectQuerySet = (
            Project.objects.filter_active()
            .order_by("status", "city__order", "name")
        )
        if self.action == self.list.__name__:
            queryset: ProjectQuerySet = (
                queryset.annotate_flats_count()
                .annotate_min_prop_price()
                .annotate_min_rooms_prices()
            )
        elif self.action == "retrieve":
            queryset: ProjectQuerySet = (
                queryset.annotate_flats_count()
                .annotate_min_prop_price()
                .annotate_min_rooms_prices()
                .annotate_prop_area_range()
                .prefetch_related(
                    Prefetch(
                        "furnish_set",
                        Furnish.objects.prefetch_related(
                            "image_set__point_set", "furnishadvantage_set", "jobdescription_set"
                        ),
                    ),
                    Prefetch(
                        "furnish_kitchen_set",
                        FurnishKitchen.objects.prefetch_related(
                            "image_set"
                        )
                    ),
                    Prefetch(
                        "furnishimage_set",
                        FurnishImage.objects.prefetch_related("point_set")
                    )
                )
            )
        elif self.action == "buildings":
            queryset: ProjectQuerySet = queryset.prefetch_related(
                Prefetch(
                    "building_set",
                    Building.objects.filter_active()
                    .annotate_min_prices()
                    .annotate_total_floor()
                    .annotate_flats_count(),
                ),
            )

        return queryset

    def get_serializer_class(self) -> Type[Serializer]:
        serializer_class: Type[Serializer] = ProjectListSerializer
        if self.action == self.retrieve.__name__:
            serializer_class: Type[Serializer] = ProjectRetrieveSerializer
        elif self.action == "buildings":
            serializer_class: Type[Serializer] = ProjectGenplanSerializer
        return serializer_class

    @action(detail=True, methods=["GET"])
    def buildings(self, request, *args, **kwargs):
        """
        Корпуса проекта для генплана
        """

        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
