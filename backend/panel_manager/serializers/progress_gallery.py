from rest_framework.serializers import ModelSerializer

from ..models import ProgressGallery


class ProgressGalleryRetrieveSerializer(ModelSerializer):
    """
    Сериализатор детального хода строительства
    """

    class Meta:
        model = ProgressGallery
        exclude = ("progress", "order")
