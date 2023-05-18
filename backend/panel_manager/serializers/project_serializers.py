from rest_framework.fields import IntegerField
from rest_framework.serializers import ModelSerializer

from common.rest_fields import MultiImageField, RoundedPriceReadOnlyField
from infras.serialzers import (MainInfraSerializer, RoundInfraSerializer,
                               SubInfraSerializer)
from panel_manager.models import ProjectBrochure
from projects.models import Project
from properties.serializers import (_FurnishFurnitureSerializer,
                                    _FurnishKitchenSerializer,
                                    _FurnishSerializer)


class ProjectBrochureSerializer(ModelSerializer):
    """Сериалиазтор брошюры проекта."""

    class Meta:
        model = ProjectBrochure
        fields = ("id", "file", )
        read_only_fields = fields


class ProjectListSerializer(ModelSerializer):
    """ Сериализатор списка проектов"""
    flats_count = IntegerField(required=False, read_only=True)
    min_flat_price_a = RoundedPriceReadOnlyField()
    min_commercial_prop_price_a = RoundedPriceReadOnlyField()
    min_commercial_tenant_price_a = RoundedPriceReadOnlyField()
    min_commercial_business_price_a = RoundedPriceReadOnlyField()

    card_image_display = MultiImageField(required=False, read_only=True)
    card_image_preview = MultiImageField(required=False, read_only=True)
    plan_display = MultiImageField(required=False, read_only=True)
    plan_preview = MultiImageField(required=False, read_only=True)
    image_panel_manager_display = MultiImageField(required=False, read_only=True)
    image_panel_manager_preview = MultiImageField(required=False, read_only=True)
    # category = ProjectCategoryShortSerializer()

    flats_0_min_price_a = RoundedPriceReadOnlyField()
    flats_1_min_price_a = RoundedPriceReadOnlyField()
    flats_2_min_price_a = RoundedPriceReadOnlyField()
    flats_3_min_price_a = RoundedPriceReadOnlyField()
    flats_4_min_price_a = RoundedPriceReadOnlyField()
    brochures = ProjectBrochureSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = (
            "id",
            "slug",
            "name",
            "latitude",
            "longitude",
            "flats_count",
            "min_flat_price_a",
            "min_commercial_prop_price_a",
            "min_commercial_tenant_price_a",
            "min_commercial_business_price_a",
            "description",
            "card_image_display",
            "card_image_preview",
            "plan_display",
            "plan_preview",
            "flats_0_min_price_a",
            "flats_1_min_price_a",
            "flats_2_min_price_a",
            "flats_3_min_price_a",
            "flats_4_min_price_a",
            "image_panel_manager_display",
            "image_panel_manager_preview",
            "brochures"
        )


class ProjectRetrieveSerializer(ModelSerializer):
    """
    Сериализатор детального проекта
    """

    flats_count = IntegerField(required=False, read_only=True)
    min_flat_price_a = RoundedPriceReadOnlyField()
    min_commercial_prop_price_a = RoundedPriceReadOnlyField()
    min_commercial_tenant_price_a = RoundedPriceReadOnlyField()
    min_commercial_business_price_a = RoundedPriceReadOnlyField()

    min_flat_area_a = IntegerField(required=False, read_only=True)
    max_flat_area_a = IntegerField(required=False, read_only=True)
    min_commercial_prop_area_a = IntegerField(required=False, read_only=True)
    max_commercial_prop_area_a = IntegerField(required=False, read_only=True)

    plan_display = MultiImageField(required=False, read_only=True)
    plan_preview = MultiImageField(required=False, read_only=True)
    image_panel_manager_display = MultiImageField(required=False, read_only=True)
    image_panel_manager_preview = MultiImageField(required=False, read_only=True)

    flats_0_min_price_a = RoundedPriceReadOnlyField()
    flats_1_min_price_a = RoundedPriceReadOnlyField()
    flats_2_min_price_a = RoundedPriceReadOnlyField()
    flats_3_min_price_a = RoundedPriceReadOnlyField()
    flats_4_min_price_a = RoundedPriceReadOnlyField()

    maininfra_set = MainInfraSerializer(many=True, read_only=True)
    subinfra_set = SubInfraSerializer(many=True, read_only=True)
    roundinfra_set = RoundInfraSerializer(many=True, read_only=True)

    furnish_set = _FurnishSerializer(many=True, read_only=True)
    furnish_kitchen_set = _FurnishKitchenSerializer(many=True, read_only=True)
    furnish_furniture_set = _FurnishFurnitureSerializer(many=True, read_only=True)
    brochures = ProjectBrochureSerializer(many=True, read_only=True, help_text="брошюры проектов")

    class Meta:
        model = Project
        fields = "__all__"
