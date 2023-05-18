from graphql_relay import to_global_id
from rest_framework import serializers

from buildings.serializers.building import BuildingSerializer
from buildings.serializers.floor import FloorSerializer
from buildings.serializers.section import SectionSerializer
from properties.serializers import _FurnishSerializer, _FurnishKitchenSerializer
from projects.serializers.project import ProjectSerializer
from properties.constants import FeatureType
from properties.models import (
    Property,
    WindowView,
    WindowViewType,
    Feature,
    WindowViewAngle,
    MiniPlanPoint,
    MiniPlanPointAngle,
    Furnish,
    FurnishImage,
    FurnishPoint,
    SpecialOffer,
    FurnishAdvantage,
    JobDescription,
    Layout,
)


class _FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        exclude = ("cities",)


class _SpecialOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialOffer
        fields = "__all__"


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
        fields = "__all__"


class _MiniPlanPointAngleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MiniPlanPointAngle
        fields = "__all__"


class _MiniPlanPointSerializer(serializers.ModelSerializer):
    miniplanpointangle_set = _MiniPlanPointAngleSerializer(many=True, read_only=True)

    class Meta:
        model = MiniPlanPoint
        fields = "__all__"


class FlatSerializer(serializers.ModelSerializer):

    status = serializers.IntegerField(required=False, read_only=True)
    completed = serializers.BooleanField(required=False, read_only=True)
    has_discount = serializers.BooleanField(required=False, read_only=True)
    is_favorite = serializers.BooleanField(required=False, read_only=True)

    infra = serializers.CharField(required=False, read_only=True)
    infra_text = serializers.CharField(required=False, read_only=True)

    min_mortgage = serializers.IntegerField(required=False, read_only=True)
    first_payment = serializers.IntegerField(required=False, read_only=True)

    building_total_floor = serializers.IntegerField(required=False, read_only=True)

    plan_3d = serializers.FileField(required=False, read_only=True)
    plan_3d_1 = serializers.FileField(required=False, read_only=True)
    plan_png = serializers.FileField(required=False, read_only=True)
    plan_png_preview = serializers.FileField(required=False, read_only=True)
    bank_logo_1 = serializers.FileField(required=False, read_only=True)
    bank_logo_2 = serializers.FileField(required=False, read_only=True)
    plan = serializers.FileField(required=False, read_only=True)
    commercial_plan = serializers.FileField(required=False, read_only=True)

    repair_color_name = serializers.CharField(required=False, read_only=True)
    repair_color_hex = serializers.CharField(required=False, read_only=True)
    booking_days = serializers.IntegerField(required=False, read_only=True)

    project = ProjectSerializer(read_only=True, many=False)
    building = BuildingSerializer(read_only=True, many=False)
    section = SectionSerializer(read_only=True, many=False)
    floor = FloorSerializer(read_only=True, many=False)
    window_view = _WindowViewsSerializer(many=False, read_only=True)

    features = serializers.SerializerMethodField()

    mini_plan_point = _MiniPlanPointSerializer(many=False, read_only=True)

    graphql_id = serializers.SerializerMethodField()
    furnishSet = _FurnishSerializer(many=True, read_only=True, source="furnish_set")
    furnishKitchenSet = _FurnishKitchenSerializer(many=True, read_only=True, source="furnish_kitchen_set")

    specialOffers = _SpecialOfferSerializer(many=True, read_only=True, source="special_offers")

    class Meta:
        model = Property
        exclude = ("purposes", "update_text", "update_time", "changed")

    def get_features(self, obj: Property):
        kinds = []
        for kind in FeatureType.values:
            if getattr(obj, kind, False):
                kinds.append(kind)
        qs = Feature.objects.filter(
            filter_show=True, property_kind__contains=[obj.type], kind__in=kinds
        )
        serializer = _FeatureSerializer(qs, many=True, read_only=True)
        return serializer.data

    def get_graphql_id(self, obj: Property):
        return to_global_id("GlobalFlatType", str(obj.id))


class FlatListSerializer(serializers.ModelSerializer):

    status = serializers.IntegerField(required=False, read_only=True)
    completed = serializers.BooleanField(required=False, read_only=True)
    has_discount = serializers.BooleanField(required=False, read_only=True)
    is_favorite = serializers.BooleanField(required=False, read_only=True)

    infra = serializers.CharField(required=False, read_only=True)
    infra_text = serializers.CharField(required=False, read_only=True)

    min_mortgage = serializers.IntegerField(required=False, read_only=True)
    first_payment = serializers.IntegerField(required=False, read_only=True)

    building_total_floor = serializers.IntegerField(required=False, read_only=True)

    plan_3d = serializers.FileField(required=False, read_only=True)
    plan_png = serializers.FileField(required=False, read_only=True)
    plan_png_preview = serializers.FileField(required=False, read_only=True)
    bank_logo_1 = serializers.FileField(required=False, read_only=True)
    bank_logo_2 = serializers.FileField(required=False, read_only=True)
    plan = serializers.FileField(required=False, read_only=True)
    commercial_plan = serializers.FileField(required=False, read_only=True)

    repair_color_name = serializers.CharField(required=False, read_only=True)
    repair_color_hex = serializers.CharField(required=False, read_only=True)
    booking_days = serializers.IntegerField(required=False, read_only=True)

    # project = ProjectSerializer(read_only=True, many=False)
    # building = BuildingSerializer(read_only=True, many=False)
    # section = SectionSerializer(read_only=True, many=False)
    floor = FloorSerializer(read_only=True, many=False)
    # window_view = _WindowViewsSerializer(many=False, read_only=True)

    # features = serializers.SerializerMethodField()

    # mini_plan_point = _MiniPlanPointSerializer(many=False, read_only=True)

    graphql_id = serializers.SerializerMethodField()
    # furnishSet = _FurnishSerializer(many=True, read_only=True, source="furnish_set")

    # specialOffers = _SpecialOfferSerializer(many=True, read_only=True, source="special_offers")

    class Meta:
        model = Property
        exclude = ("purposes", "update_text", "update_time", "changed")

    def get_features(self, obj: Property):
        kinds = []
        for kind in FeatureType.values:
            if getattr(obj, kind, False):
                kinds.append(kind)
        qs = Feature.objects.filter(
            filter_show=True, property_kind__contains=[obj.type], kind__in=kinds
        )
        serializer = _FeatureSerializer(qs, many=True, read_only=True)
        return serializer.data

    def get_graphql_id(self, obj: Property):
        return to_global_id("GlobalFlatType", str(obj.id))
