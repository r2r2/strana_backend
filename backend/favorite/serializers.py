from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer, ReadOnlyField, CharField, FloatField

from common.rest_fields import MultiImageField
from properties.constants import PropertyType
from properties.models import Property
from users.models import UserLikeProperty


class FavoritesCreateSerializer(ModelSerializer):
    meeting_id = CharField(label="ID встречи", required=False, allow_null=True)

    class Meta:
        model = UserLikeProperty
        fields = ("property", "meeting_id")

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs["user"] = self.context["request"].user
        return attrs


class FavoritesListSerializer(ModelSerializer):
    project_id = ReadOnlyField(source="project.id")
    project_slug = ReadOnlyField(source="project.slug")
    project_name = ReadOnlyField(source="project.name")
    hide_price = ReadOnlyField(source="project.hide_price")
    disable_booking = ReadOnlyField(source="project.disable_booking")
    floor = ReadOnlyField(source="floor.number")
    layout_name = ReadOnlyField(source="layout.name")
    plan_furn_display = MultiImageField()
    plan_furn_preview = MultiImageField()
    plan_3d_display = MultiImageField()
    plan_3d_preview = MultiImageField()
    total_floors = ReadOnlyField(source="section.total_floors")
    building_id = ReadOnlyField(source="building.id")
    building_name = ReadOnlyField(source="building.name")
    building_number = ReadOnlyField(source="building.number")
    completion_year = ReadOnlyField(source="building.completion_year")
    completion_quarter = ReadOnlyField(source="building.completion_quarter")
    min_mortgage = FloatField(read_only=True)
    address_city = CharField(source="project.address_city", read_only=True)
    section_number = ReadOnlyField(source="section.number")
    type = SerializerMethodField()
    furnish_display = ReadOnlyField()

    class Meta:
        model = Property
        fields = (
            "id",
            "number",
            "article",
            "area",
            "project_id",
            "project_slug",
            "project_name",
            "plan",
            "floor",
            "number_on_floor",
            "price",
            "original_price",
            "status",
            "type",
            "layout_name",
            "rooms",
            "plan_furn_display",
            "plan_furn_preview",
            "plan_3d_display",
            "plan_3d_preview",
            "furnish",
            "total_floors",
            "building_id",
            "building_name",
            "building_number",
            "completion_year",
            "completion_quarter",
            "min_mortgage",
            "address_city",
            "section_number",
            "metros",
            "hide_price",
            "disable_booking",
            "furnish_display",
            "tags",
        )

    @staticmethod
    def get_type(obj):
        if obj.type == PropertyType.FLAT:
            return "flats"
        else:
            return obj.type
