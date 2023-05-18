from rest_framework.serializers import ModelSerializer

from common.rest_fields import MultiImageField, RoundedPriceReadOnlyField
from properties.models import (
    Furnish,
    FurnishImage,
    FurnishPoint,
    JobDescription,
    JobDescriptionKitchen,
    FurnishAdvantage,
    FurnishKitchen,
    FurnishKitchenAdvantage,
    FurnishKitchenPoint,
    FurnishKitchenImage,
)


class _JobDescriptionKitchenSerializer(ModelSerializer):
    imageDisplay = MultiImageField(required=False, read_only=True, source="image_display")
    imagePreview = MultiImageField(required=False, read_only=True, source="image_preview")

    class Meta:
        model = JobDescriptionKitchen
        exclude = ("furnish",)


class _FurnishKitchenAdvantageSerializer(ModelSerializer):
    imageDisplay = MultiImageField(required=False, read_only=True, source="image_display")
    imagePreview = MultiImageField(required=False, read_only=True, source="image_preview")

    class Meta:
        model = FurnishKitchenAdvantage
        fields = "__all__"


class _FurnishKitchenPointSerializer(ModelSerializer):
    class Meta:
        model = FurnishKitchenPoint
        fields = "__all__"


class _FurnishKitchenImageSerializer(ModelSerializer):
    fileDisplay = MultiImageField(required=False, read_only=True, source="file_display")
    filePreview = MultiImageField(required=False, read_only=True, source="file_preview")
    pointSet = _FurnishKitchenPointSerializer(
        many=True, required=False, read_only=True, source="point_set"
    )

    class Meta:
        model = FurnishKitchenImage
        fields = "__all__"


class _FurnishKitchenSerializer(ModelSerializer):
    imageSet = _FurnishKitchenImageSerializer(many=True, read_only=True, source="image_set")
    furnishadvantageSet = _FurnishKitchenAdvantageSerializer(
        many=True, read_only=True, source="furnishadvantage_set"
    )
    jobdescriptionSet = _JobDescriptionKitchenSerializer(
        many=True, read_only=True, source="jobdescription_set"
    )

    class Meta:
        model = FurnishKitchen
        fields = "__all__"
