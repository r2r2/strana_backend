from http import HTTPStatus
from typing import Type, Any

from django.db.models import Prefetch
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import FilterSet, DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, BasePermission
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import ReadOnlyModelViewSet

from news.constants import NewsType
from news.models import News, NewsSlide
from ..filters import ProgressFilter, CameraFilter
from ..models import Camera
from ..querysets import ProgressQuerySet
from ..serializers import (
    CameraListSerializer,
    ProgressNewsListSerializer,
    ProgressNewsRetrieveSerializer,
)


class PanelManagerProgressViewSet(ReadOnlyModelViewSet):
    """
    Ходы строительства
    """

    pagination_class = None
    permission_classes: tuple[Type[BasePermission]] = (AllowAny,)
    filterset_class: Type[FilterSet] = ProgressFilter
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self) -> ProgressQuerySet:
        queryset = (
            News.objects.annotate_color()
            .filter(type=NewsType.PROGRESS, date__isnull=False, published=True)
            .filter_timeframed()
            .annotate_quarter()
            .annotate_year()
            .annotate_month()
            .prefetch_related(
                Prefetch("newsslide_set", NewsSlide.objects.select_related("building"))
            )
            .order_by("-year", "-month_number")
        )
        return queryset

    def get_serializer_class(self) -> Type[Serializer]:
        serializer_class: Type[Serializer] = ProgressNewsListSerializer
        if self.action == self.retrieve.__name__:
            serializer_class: Type[Serializer] = ProgressNewsRetrieveSerializer
        return serializer_class

    @action(detail=False, methods=["GET"])
    def specs(self, request: Request, *args: list[Any], **kwargs: dict[Any, Any]) -> Response:
        queryset: ProgressQuerySet = self.get_queryset()
        filter: ProgressFilter = self.filterset_class(
            self.request.query_params, self.filterset_class(self.request.query_params, queryset).qs
        )
        data: Any = filter.specs()
        return Response(data=data, status=HTTPStatus.OK)

    @action(detail=False, methods=["GET"])
    def facets(self, request: Request, *args: list[Any], **kwargs: dict[Any, Any]) -> Response:
        queryset: ProgressQuerySet = self.get_queryset()
        filter: ProgressFilter = self.filterset_class(self.request.query_params, queryset)
        data: Any = filter.facets()
        data["timeline"] = filter.qs.timeline_serialized()
        return Response(data=data, status=HTTPStatus.OK)

    @method_decorator(cache_page(60 * 60 * 2))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class PanelManagerCameraViewSet(ReadOnlyModelViewSet):
    """
    Камеры
    """

    queryset = Camera.objects.filter(active=True)
    serializer_class: Type[Serializer] = CameraListSerializer
    permission_classes: tuple[Type[BasePermission]] = (AllowAny,)
    filterset_class: Type[FilterSet] = CameraFilter
