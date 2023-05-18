from rest_framework.serializers import ModelSerializer
from ..models import Camera


class CameraListSerializer(ModelSerializer):
    """
    Сериализатор списка камер
    """

    class Meta:
        model = Camera
        exclude = ("order", "project")
