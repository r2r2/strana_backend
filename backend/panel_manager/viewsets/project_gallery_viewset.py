from rest_framework.viewsets import ReadOnlyModelViewSet

from ..models import AboutProjectGallery
from ..serializers import AboutProjectGalleryForSlidesSeriazlier


class PanelManagerProjectGalleryViewSet(ReadOnlyModelViewSet):
    """
    Галлерея проектов
    """

    serializer_class = AboutProjectGalleryForSlidesSeriazlier
    queryset = AboutProjectGallery.objects.select_related("category")
    pagination_class = None
