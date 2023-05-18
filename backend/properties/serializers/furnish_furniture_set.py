from rest_framework.serializers import ModelSerializer

from common.rest_fields import MultiImageField, RoundedPriceReadOnlyField
from properties.models import (
    Furnish,
    FurnishImage,
    FurnishPoint,
    JobDescription,
    JobDescriptionFurniture,
    FurnishAdvantage,
    FurnishFurniture,
    FurnishFurnitureAdvantage,
    FurnishFurniturePoint,
    FurnishFurnitureImage,
)


class _JobDescriptionFurnitureSerializer(ModelSerializer):
    imageDisplay = MultiImageField(required=False, read_only=True, source="image_display")
    imagePreview = MultiImageField(required=False, read_only=True, source="image_preview")

    class Meta:
        model = JobDescriptionFurniture
        exclude = ("furnish",)


class _FurnishFurnitureAdvantageSerializer(ModelSerializer):
    imageDisplay = MultiImageField(required=False, read_only=True, source="image_display")
    imagePreview = MultiImageField(required=False, read_only=True, source="image_preview")

    class Meta:
        model = FurnishFurnitureAdvantage
        fields = "__all__"


class _FurnishFurniturePointSerializer(ModelSerializer):
    class Meta:
        model = FurnishFurniturePoint
        fields = "__all__"


class _FurnishFurnitureImageSerializer(ModelSerializer):
    fileDisplay = MultiImageField(required=False, read_only=True, source="file_display")
    filePreview = MultiImageField(required=False, read_only=True, source="file_preview")
    pointSet = _FurnishFurniturePointSerializer(
        many=True, required=False, read_only=True, source="point_set"
    )

    class Meta:
        model = FurnishFurnitureImage
        fields = "__all__"


class _FurnishFurnitureSerializer(ModelSerializer):
    imageSet = _FurnishFurnitureImageSerializer(many=True, read_only=True, source="image_set")
    furnishadvantageSet = _FurnishFurnitureAdvantageSerializer(
        many=True, read_only=True, source="furnishadvantage_set"
    )
    jobdescriptionSet = _JobDescriptionFurnitureSerializer(
        many=True, read_only=True, source="jobdescription_set"
    )

    class Meta:
        model = FurnishFurniture
        fields = "__all__"
