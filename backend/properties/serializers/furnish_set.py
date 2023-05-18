from rest_framework.serializers import ModelSerializer

from common.rest_fields import MultiImageField, RoundedPriceReadOnlyField
from properties.models import (
    Furnish,
    FurnishImage,
    FurnishPoint,
    JobDescription,
    FurnishAdvantage,
    FurnishKitchen,
    FurnishKitchenAdvantage,
    FurnishKitchenPoint,
    FurnishKitchenImage,
)

class _JobDescriptionSerializer(ModelSerializer):
    imageDisplay = MultiImageField(required=False, read_only=True, source="image_display")
    imagePreview = MultiImageField(required=False, read_only=True, source="image_preview")

    class Meta:
        model = JobDescription
        exclude = ("furnish",)


class _FurnishAdvantageSerializer(ModelSerializer):
    imageDisplay = MultiImageField(required=False, read_only=True, source="image_display")
    imagePreview = MultiImageField(required=False, read_only=True, source="image_preview")

    class Meta:
        model = FurnishAdvantage
        fields = "__all__"


class _FurnishPointSerializer(ModelSerializer):
    class Meta:
        model = FurnishPoint
        fields = "__all__"


class _FurnishImageSerializer(ModelSerializer):
    fileDisplay = MultiImageField(required=False, read_only=True, source="file_display")
    filePreview = MultiImageField(required=False, read_only=True, source="file_preview")
    pointSet = _FurnishPointSerializer(
        many=True, required=False, read_only=True, source="point_set"
    )

    class Meta:
        model = FurnishImage
        fields = "__all__"


class _FurnishSerializer(ModelSerializer):
    imageSet = _FurnishImageSerializer(many=True, read_only=True, source="image_set")
    furnishadvantageSet = _FurnishAdvantageSerializer(
        many=True, read_only=True, source="furnishadvantage_set"
    )
    jobdescriptionSet = _JobDescriptionSerializer(
        many=True, read_only=True, source="jobdescription_set"
    )

    class Meta:
        model = Furnish
        fields = "__all__"