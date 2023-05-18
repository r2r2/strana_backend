from typing import Type

from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import BasePermission, AllowAny
from rest_framework.viewsets import ModelViewSet

from ..filters import PresentationStageFilter
from ..models import PresentationStage, AboutProjectGalleryCategory
from ..serializers import PresentationStageListSerializer


class PanelManagerPresentationStageViewSet(ModelViewSet):
    """
    Блок презентации
    ?hard_type=&project=08a75d32-90db-e811-94a5-00155d000e67
    """

    permission_classes: tuple[Type[BasePermission]] = (AllowAny,)
    queryset = PresentationStage.objects.order_by("stage_number").prefetch_related(
        Prefetch(
            "about_project_slides",
            AboutProjectGalleryCategory.objects.prefetch_related(
                "aboutprojectgallery_set__pinsaboutprojectgallery_set"
            ).order_by("presentationsteps__order"),
        )
    )
    serializer_class = PresentationStageListSerializer
    filterset_class = PresentationStageFilter
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)

