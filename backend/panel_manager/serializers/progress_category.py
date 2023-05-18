from rest_framework.serializers import ModelSerializer

from common.rest_fields import MultiImageField
from .progress_gallery import ProgressGalleryRetrieveSerializer
from ..models import ProgressCategory


class ProgressCategoryListSerializer(ModelSerializer):
    """
    Сериализатор списка ходов строительства
    """

    progressgallery_set = ProgressGalleryRetrieveSerializer(
        required=False, read_only=True, many=True
    )

    class Meta:
        model = ProgressCategory
        fields = "__all__"
