from graphql_relay import to_global_id
from rest_framework import serializers

from buildings.models import Building, Floor
from common.rest_fields import MultiImageField
from projects.models import Project
from properties.models import Layout, WindowView, WindowViewAngle, WindowViewType


class _ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        exclude = ("furnish_set", "furnish_kitchen_set")


class _BuildingSerializer(serializers.ModelSerializer):
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

    class Meta:
        model = Building
        exclude = ("project", "residential_set", "booking_types", "furnish_set", "point", "plan_hover")

    def get_days_ahead(self, obj: Building):
        if obj.finish_date and obj.fact_date:
            td = obj.finish_date - obj.fact_date
            return td.days


class _FloorSerializer(serializers.ModelSerializer):
    plan = serializers.FileField(required=False, read_only=True)

    class Meta:
        model = Floor
        exclude = ("section", "point", "plan_hover")


class _WindowViewTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WindowViewType
        exclude = ("building", "section")


class _WindowViewAngleSerializer(serializers.ModelSerializer):
    class Meta:
        model = WindowViewAngle
        fields = "__all__"


class _WindowViewsSerializer(serializers.ModelSerializer):
    type = _WindowViewTypeSerializer(read_only=True)
    windowviewangle_set = _WindowViewAngleSerializer(many=True, read_only=True)

    class Meta:
        model = WindowView
        exclude = ()


class LayoutSerializer(serializers.ModelSerializer):
    plan = serializers.FileField(required=False, read_only=True)
    planoplan = serializers.FileField(required=False, read_only=True)
    floor_plan = serializers.FileField(required=False, read_only=True)
    area = serializers.IntegerField(required=False, read_only=True)
    price = serializers.IntegerField(required=False, read_only=True)
    min_price = serializers.IntegerField(required=False, read_only=True)
    original_price = serializers.IntegerField(required=False, read_only=True)
    rooms = serializers.IntegerField(required=False, read_only=True)
    max_floor = serializers.IntegerField(required=False, read_only=True, source="max_floor_a")
    min_floor = serializers.IntegerField(required=False, read_only=True, source="min_floor_a")
    flat_count = serializers.IntegerField(source='dynamic_flat_count', required=False, read_only=True)
    min_mortgage = serializers.IntegerField(required=False, read_only=True)
    first_payment = serializers.IntegerField(required=False, read_only=True)
    floor_plan_width = serializers.IntegerField(required=False, read_only=True)
    floor_plan_height = serializers.IntegerField(required=False, read_only=True)
    first_flat_id = serializers.IntegerField(required=False, read_only=True)

    facing = serializers.BooleanField(required=False, read_only=True)
    has_view = serializers.BooleanField(required=False, read_only=True)
    frontage = serializers.BooleanField(required=False, read_only=True)
    is_duplex = serializers.BooleanField(required=False, read_only=True)
    has_parking = serializers.BooleanField(required=False, read_only=True)
    has_terrace = serializers.BooleanField(required=False, read_only=True)
    installment = serializers.BooleanField(required=False, read_only=True)
    maternal_capital = serializers.BooleanField(required=False, read_only=True)
    has_high_ceiling = serializers.BooleanField(required=False, read_only=True)
    has_action_parking = serializers.BooleanField(required=False, read_only=True)
    has_two_sides_windows = serializers.BooleanField(required=False, read_only=True)
    has_panoramic_windows = serializers.BooleanField(required=False, read_only=True)
    preferential_mortgage4 = serializers.BooleanField(required=False, read_only=True)
    hypo_popular = serializers.BooleanField(required=False, read_only=True)

    plan_hover = serializers.CharField(required=False, read_only=True)
    completion_date = serializers.CharField(required=False, read_only=True)
    floor_plan_hover = serializers.CharField(required=False, read_only=True)

    project = _ProjectSerializer(many=False, read_only=True)
    building = _BuildingSerializer(many=False, read_only=True)
    floor = _FloorSerializer(many=False, read_only=True)
    window_view = _WindowViewsSerializer(many=False, read_only=True)

    class Meta:
        model = Layout
        fields = "__all__"
