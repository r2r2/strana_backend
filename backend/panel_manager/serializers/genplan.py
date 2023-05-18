from rest_framework.fields import IntegerField, FileField, SerializerMethodField
from rest_framework.serializers import ModelSerializer

from buildings.models import Building, GroupSection, Section, Floor
from common.rest_fields import MultiImageField
from panel_manager.serializers import FlatSerializer
from projects.models import Project


class BuildingProjectSerializer(ModelSerializer):
    plan = FileField(required=False, read_only=True)
    plan_display = MultiImageField(required=False, read_only=True)
    plan_preview = MultiImageField(required=False, read_only=True)

    commercial_plan = FileField(required=False, read_only=True)
    commercial_plan_display = MultiImageField(required=False, read_only=True)
    commercial_plan_preview = MultiImageField(required=False, read_only=True)

    window_view_plan = FileField(required=False, read_only=True)
    window_view_plan_display = MultiImageField(required=False, read_only=True)
    window_view_plan_preview = MultiImageField(required=False, read_only=True)

    window_view_plan_lot_display = MultiImageField(required=False, read_only=True)
    window_view_plan_lot_preview = MultiImageField(required=False, read_only=True)

    mini_plan = FileField(required=False, read_only=True)

    flats_count = IntegerField()
    total_floor = IntegerField()

    class Meta:
        model = Building
        fields = "__all__"


class ProjectGenplanSerializer(ModelSerializer):
    """
    Сериализатор проекта для генплана
    """

    plan_display = MultiImageField(required=False, read_only=True)
    plan_preview = MultiImageField(required=False, read_only=True)
    building_set = BuildingProjectSerializer(many=True)

    class Meta:
        model = Project
        fields = (
            "slug",
            "name",
            "plan_display",
            "plan_preview",
            "plan_width",
            "plan_height",
            "building_set",
        )


class GroupSectionBuildingSerializer(ModelSerializer):
    plan = FileField()

    class Meta:
        model = GroupSection
        exclude = ("building",)


class FloorSectionSerializer(ModelSerializer):
    plan = FileField()

    flats_count = SerializerMethodField()
    parking_count = SerializerMethodField()
    commercial_count = SerializerMethodField()

    class Meta:
        model = Floor
        fields = "__all__"

    def get_flats_count(self, obj: Floor):
        return getattr(obj, "flats_count", 0)

    def get_parking_count(self, obj: Floor):
        return getattr(obj, "parking_count", 0)

    def get_commercial_count(self, obj: Floor):
        return getattr(obj, "commercial_count", 0)


class SectionGenplanSerializer(ModelSerializer):

    total_floor = IntegerField()
    flats_count = IntegerField()

    plan = FileField()

    floor_set = FloorSectionSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        fields = "__all__"


class FloorGenplanSerializer(ModelSerializer):

    flats_count = SerializerMethodField()
    parking_count = SerializerMethodField()
    commercial_count = SerializerMethodField()

    plan = FileField()

    property_set = FlatSerializer(many=True, read_only=True)

    class Meta:
        model = Floor
        fields = "__all__"

    def get_flats_count(self, obj: Floor):
        return getattr(obj, "flats_count", 0)

    def get_parking_count(self, obj: Floor):
        return getattr(obj, "parking_count", 0)

    def get_commercial_count(self, obj: Floor):
        return getattr(obj, "commercial_count", 0)


class SectionBuildingSerializer(ModelSerializer):

    total_floor = IntegerField()
    flats_count = IntegerField()

    plan = FileField()

    class Meta:
        model = Section
        exclude = ("building", "group", "point")


class BuildingSectionGroupGenplanSerializer(ModelSerializer):
    plan = FileField(required=False, read_only=True)
    plan_display = MultiImageField(required=False, read_only=True)
    plan_preview = MultiImageField(required=False, read_only=True)

    commercial_plan = FileField(required=False, read_only=True)
    commercial_plan_display = MultiImageField(required=False, read_only=True)
    commercial_plan_preview = MultiImageField(required=False, read_only=True)

    window_view_plan = FileField(required=False, read_only=True)
    window_view_plan_display = MultiImageField(required=False, read_only=True)
    window_view_plan_preview = MultiImageField(required=False, read_only=True)

    window_view_plan_lot_display = MultiImageField(required=False, read_only=True)
    window_view_plan_lot_preview = MultiImageField(required=False, read_only=True)

    mini_plan = FileField(required=False, read_only=True)

    groupsection_set = GroupSectionBuildingSerializer(many=True, read_only=True)
    section_set = SectionBuildingSerializer(many=True, read_only=True)

    flats_count = SerializerMethodField()
    parking_count = SerializerMethodField()
    commercial_count = SerializerMethodField()

    class Meta:
        model = Building
        exclude = ("furnish_set", "booking_types", "residential_set", "furnish_kitchen_set")

    def get_flats_count(self, obj: Building):
        return getattr(obj, "flats_count", 0)

    def get_parking_count(self, obj: Building):
        return getattr(obj, "parking_count", 0)

    def get_commercial_count(self, obj: Building):
        return getattr(obj, "commercial_count", 0)
