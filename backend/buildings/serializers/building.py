from rest_framework import serializers

from common.rest_fields import MultiImageField
from properties.serializers import _FurnishSerializer, _FurnishKitchenSerializer, _FurnishFurnitureSerializer

from ..models import Building


class BuildingSerializer(serializers.ModelSerializer):
    plan = serializers.FileField(required=False, read_only=True)
    plan_display = MultiImageField(required=False, read_only=True)
    plan_preview = MultiImageField(required=False, read_only=True)

    commercial_plan = serializers.FileField(required=False, read_only=True)
    commercial_plan_display = MultiImageField(required=False, read_only=True)
    commercial_plan_preview = MultiImageField(required=False, read_only=True)

    window_view_plan = serializers.FileField(required=False, read_only=True)
    window_view_plan_display = MultiImageField(required=False, read_only=True)
    window_view_plan_preview = MultiImageField(required=False, read_only=True)

    window_view_plan_lot_display = MultiImageField(required=False, read_only=True)
    window_view_plan_lot_preview = MultiImageField(required=False, read_only=True)

    mini_plan = serializers.FileField(required=False, read_only=True)

    days_ahead = serializers.SerializerMethodField()
    furnishSet = _FurnishSerializer(many=True, read_only=True, source="furnish_set")
    furnishKitchenSet = _FurnishKitchenSerializer(many=True, read_only=True, source="furnish_kitchen_set")
    furnishFurnitureSet = _FurnishFurnitureSerializer(many=True, read_only=True, source="furnish_furniture_set")

    class Meta:
        model = Building
        exclude = ("project", "residential_set")

    def get_days_ahead(self, obj: Building):
        if obj.finish_date and obj.fact_date:
            td = obj.finish_date - obj.fact_date
            return td.days
