from rest_framework import serializers
from common.rest_fields import MultiImageField

from ..models import Project, ProjectFeature


class _ProjectFeatureSerializer(serializers.ModelSerializer):
    imageDisplay = MultiImageField(required=False, read_only=True, source="image_display")
    imagePreview = MultiImageField(required=False, read_only=True, source="image_preview")

    class Meta:
        model = ProjectFeature
        fields = "__all__"


class ProjectSerializer(serializers.ModelSerializer):
    card_image_display = MultiImageField(required=False, read_only=True)
    card_image_preview = MultiImageField(required=False, read_only=True)

    plan_display = MultiImageField(required=False, read_only=True)
    plan_preview = MultiImageField(required=False, read_only=True)
    image_panel_manager_display = MultiImageField(required=False, read_only=True)
    image_panel_manager_preview = MultiImageField(required=False, read_only=True)
    projectfeatureSet = _ProjectFeatureSerializer(
        many=True, read_only=True, source="projectfeature_set"
    )

    class Meta:
        model = Project
        exclude = ("furnish_set", "furnish_kitchen_set", "furnish_furniture_set")
