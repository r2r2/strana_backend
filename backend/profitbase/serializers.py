from typing import Optional, Tuple

from django.db.models import Max
from django.utils.timezone import now
from rest_framework import serializers

from buildings.constants import BuildingType
from buildings.models import Building, Floor, Section
from projects.models import Project
from properties.constants import FeatureType, PropertyStatus, PropertyType
from properties.models import *

from . import logger
from .constants import CONVERT_STATUS_MAP, CONVERT_TYPE_MAP
from .utils import parse_bool, parse_datetime, parse_int


class BuildingAddressProfitBaseSerializer(serializers.Serializer):
    """
    Серализатор адреса корпуса из profitbase
    """

    full = serializers.CharField(
        required=False, allow_null=True, allow_blank=True, max_length=500, read_only=False
    )
    locality = serializers.CharField(
        required=False, allow_null=True, allow_blank=True, max_length=500, read_only=False
    )
    district = serializers.CharField(
        required=False, allow_null=True, allow_blank=True, max_length=500, read_only=False
    )
    region = serializers.CharField(
        required=False, allow_null=True, allow_blank=True, max_length=500, read_only=False
    )
    street = serializers.CharField(
        required=False, allow_null=True, allow_blank=True, max_length=500, read_only=False
    )
    number = serializers.CharField(
        required=False, allow_null=True, allow_blank=True, max_length=500, read_only=False
    )


class ProjectProfitBaseSerializer(serializers.ModelSerializer):
    """
    Сериализатор проекта из profitbase
    """

    id = serializers.IntegerField()
    title = serializers.CharField(source="name")

    class Meta:
        model = Project
        fields = ("id", "title")


class BuildingProfitBaseSerializer(serializers.ModelSerializer):
    """
    Сериализатор корпуса из profitbase
    """

    id = serializers.IntegerField()
    address = BuildingAddressProfitBaseSerializer(required=False, read_only=False)
    is_active = serializers.BooleanField(required=False)
    title = serializers.CharField(source="name")
    projectId = serializers.IntegerField(source="project_id")
    type = serializers.ChoiceField(BuildingType.choices, source="kind")

    def to_internal_value(self, data):
        ret = super().to_internal_value(data)
        address = ret["address"]
        city = address.get("locality", "Москва")
        street = address.get("street", "Двинская")
        number = address.get("number", "6")
        ret["address"] = f"г. {city}, ул. {street}, {number}"
        return ret

    class Meta:
        model = Building
        fields = ("id", "is_active", "projectId", "type", "title", "address")


class PropertyProfitBaseSerializer(serializers.ModelSerializer):
    """
    Сериализатор объекта недвижимости из profitbase
    """

    id = serializers.IntegerField()
    area_total = serializers.FloatField(source="area", required=False)
    project_id = serializers.IntegerField(required=False)
    house_id = serializers.IntegerField(source="building_id", required=False)
    floor = serializers.IntegerField(required=False)
    section = serializers.CharField(required=False, allow_blank=True)
    custom_fields = serializers.ListField()
    specialOffers = serializers.ListField()
    status = serializers.CharField()
    propertyType = serializers.CharField(required=False, source="type")
    studio = serializers.BooleanField()
    rooms_amount = serializers.IntegerField(source="rooms")
    description = serializers.CharField(required=False)

    class Meta:
        model = Property
        fields = (
            "id",
            "number",
            "area_total",
            "house_id",
            "floor",
            "section",
            "custom_fields",
            "specialOffers",
            "status",
            "propertyType",
            "project_id",
            "studio",
            "rooms_amount",
            "description",
            "profitbase_id"
        )

    def to_internal_value(self, data):
        ret = super().to_internal_value(data)
        ret["update_text"] = str(ret)
        ret["update_time"] = now()
        ret["profitbase_id"] = data["id"]
        custom_fields = ret.pop("custom_fields", None)
        special_offers = ret.pop("specialOffers", None)
        floor_number = ret.pop("floor")
        building_id = ret.get("building_id")
        section_number = ret.pop("section")
        try:
            floor_data = next(section for section in data["floor_count_data"] if section["title"] == section_number)
        except StopIteration:
            logger.debug(f"Не удалось получить информацию об этажности")
            logger.debug(f"building_id: {building_id}")
            qs = Floor.objects.filter(
                section__building=building_id
            ).values("number").annotate(max=Max("number")).values("max").order_by("-max").last()
            if not qs:
                if data["floor_count_data"] and data["floor_count_data"][0]:
                    qs = {"max": data["floor_count_data"][0].get("count", 1)}
                else:
                    qs = {"max": 1}
            floor_data = {
                "count": qs["max"]
            }
        section_params = {
            "building_id": building_id,
            "number": section_number
        }
        section = Section.objects.filter(building_id=building_id, number=section_number).last()
        if not section:
            section = Section.objects.create(
                building_id=building_id, number=section_number, total_floors=floor_data["count"]
            )
        if section.total_floors != floor_data["count"]:
            section_params.update({"total_floors": floor_data["count"]})
        Section.objects.filter(pk=section.pk).update(**section_params)
        ret["section_id"] = section.pk
        floor, _ = Floor.objects.get_or_create(section=section, number=floor_number)
        ret["floor_id"] = floor.pk
        self.custom_fields = {field["id"]: field["value"] for field in custom_fields}
        ret["original_price"] = self.custom_fields["property_price"] or 0
        ret["price_per_meter"] = self.custom_fields["price_meter"] or 0
        ret["number_on_floor"] = self.custom_fields["position_on_floor"] or 0
        ret["status"] = CONVERT_STATUS_MAP.get(ret["status"], PropertyStatus.SOLD)
        ret["type"] = CONVERT_TYPE_MAP.get(ret["type"], PropertyType.FLAT)
        if ret["studio"]:
            ret["rooms"] = 0
        del ret["studio"]
        if ret["type"] == PropertyType.FLAT:
            ret["frontage"] = parse_bool(self.custom_fields.get("pbcf_6006d56a29436"))
        ret["preferential_mortgage"] = parse_bool(self.custom_fields.get("pbcf_6046f9fd5cb5e"))
        ret["preferential_mortgage4"] = parse_bool(self.custom_fields.get("pbcf_60f7aca8c1142"))
        ret["corner_windows"] = parse_bool(self.custom_fields.get("pbcf_5f2a8e1b07684"))
        ret["installment"] = parse_bool(self.custom_fields.get("pbcf_60221b7dd80e9"))
        ret["article"] = self.custom_fields.get("pbcf_5bb199f6a65fb") or ""
        ret["description"] = self.custom_fields.get("description") or ""
        ret["has_parking"] = parse_bool(self.custom_fields.get("pbcf_5bc80b88068ac"))
        parking = self.custom_fields.get("pbcf_5bc80b88068ac") or ""
        if parking and '/' in parking:
            parking = ''.join([s for s in parking.split('/')[1] if s.isdigit()])
        ret["parking"] = parking
        ret["has_action_parking"] = parse_bool(self.custom_fields.get("pbcf_60d3265fb79b0"))
        ret["has_view"] = parse_bool(self.custom_fields.get("pbcf_5bc80b96e4a46"))
        ret["has_terrace"] = parse_bool(self.custom_fields.get("pbcf_5bc80ba2a311a"))
        ret["is_duplex"] = parse_bool(self.custom_fields.get("pbcf_5cb99f879d5cf"))
        ret["has_high_ceiling"] = parse_bool(self.custom_fields.get("pbcf_5d78b9c63a6d4"))
        ret["has_panoramic_windows"] = parse_bool(self.custom_fields.get("pbcf_5d78b9ea0f34c"))
        ret["has_two_sides_windows"] = parse_bool(self.custom_fields.get("pbcf_5d78b9fca3ba0"))
        ret["loggias_count"] = parse_int(self.custom_fields.get("pbcf_5f2a864a0a57a"))
        ret["balconies_count"] = parse_int(self.custom_fields.get("pbcf_5f2a866729551"))
        ret["stores_count"] = parse_int(self.custom_fields.get("pbcf_5f2a8762c996e"))
        ret["wardrobes_count"] = parse_int(self.custom_fields.get("pbcf_5f2a874a73c72"))
        ret["planoplan"] = self.custom_fields.get("pbcf_5cb9a523bd89a") or ""
        ret["facing"] = parse_bool(self.custom_fields.get("pbcf_5ec4c4c06def6"))
        ret["maternal_capital"] = parse_bool(self.custom_fields.get("pbcf_60f8026b8cb55"))
        ret["has_separate_entrance"] = parse_bool(self.custom_fields.get("pbcf_610151234ba57"))
        ret["has_two_entrances"] = parse_bool(self.custom_fields.get("pbcf_610151304ac35"))
        ret["has_stained_glass"] = parse_bool(self.custom_fields.get("pbcf_61015114784a5"))
        ret["has_functional_layout"] = parse_bool(self.custom_fields.get("pbcf_610150fbef522"))
        ret["has_place_for_ads"] = parse_bool(self.custom_fields.get("pbcf_610151079d518"))
        ret["has_ceiling_three_meters"] = parse_bool(self.custom_fields.get("pbcf_610150d497c46"))
        ret["has_water_supply"] = parse_bool(self.custom_fields.get("pbcf_610150e532089"))
        ret["has_dot_two_kilowatts"] = parse_bool(self.custom_fields.get("pbcf_610150c760724"))
        ret["has_own_ventilation"] = parse_bool(self.custom_fields.get("pbcf_610150ad8aac9"))
        ret["view_cathedral"] = parse_bool(self.custom_fields.get("pbcf_6188c3455d663"))
        ret["view_gulf"] = parse_bool(self.custom_fields.get("pbcf_6188c33359e6e"))
        ret["view_river"] = parse_bool(self.custom_fields.get("pbcf_6188c322a9f70"))
        ret["view_park"] = parse_bool(self.custom_fields.get("pbcf_61890797be2d1"))
        ret["view_temple"] = parse_bool(self.custom_fields.get("pbcf_61890765c46ce"))
        ret["view_square"] = parse_bool(self.custom_fields.get("pbcf_61890774afef6"))
        ret["view_center"] = parse_bool(self.custom_fields.get("pbcf_618907581907f"))
        ret["master_bedroom"] = parse_bool(self.custom_fields.get("pbcf_5ec6619e98f80"))
        ret["is_euro_layout"] = parse_bool(self.custom_fields.get("is_euro_layout"))
        ret["smart_house"] = parse_bool(self.custom_fields.get("pbcf_61f7a9f75dba1"))

        ret["is_penthouse"] = parse_bool(self.custom_fields.get("pbcf_624179b68204c"))
        ret["is_angular"] = parse_bool(self.custom_fields.get("pbcf_5d78b9da864a9"))
        ret["is_auction"] = parse_bool(self.custom_fields.get("pbcf_60588891782e5"))
        ret["is_pantry"] = parse_bool(self.custom_fields.get("pbcf_6176e2c719a0c"))
        ret['is_cityhouse'] = parse_bool(self.custom_fields.get('pbcf_6307100b76a00'))
        ret['is_bathroom_window'] = parse_bool(self.custom_fields.get('pbcf_6241797b25b05'))
        ret["furnish_price_per_meter"] = self.custom_fields.get("pbcf_5f27ad0c8e54e", None)
        ret["furnish_comfort_price_per_meter"] = self.custom_fields.get("pbcf_62a1afdebf7db", None)
        ret["furnish_business_price_per_meter"] = self.custom_fields.get("pbcf_62a1aff705649", None)
        ret["kitchen_price"] = self.custom_fields.get("pbcf_62bd58b192914", None)
        ret["no_balcony_and_terrace_area"] = self.custom_fields.get("pbcf_5bebf0a9d0d10", None)
        ret["furniture_price"] = self.custom_fields.get("pbcf_62f105df18cd3", None)
        float_fields = (
            "furnish_price_per_meter", "furnish_comfort_price_per_meter",
            "furnish_business_price_per_meter", "kitchen_price", "furniture_price",
            "no_balcony_and_terrace_area"
        )
        for field in float_fields:
            try:
                ret[field] = float(str(ret.get(field, 0.0)).replace(",", ".")) if ret[field] else 0.0
            except ValueError:
                ret[field] = 0.0
        ret["plan_code"] = self.custom_fields["code"] if self.custom_fields["code"] else ""
        if ret["article"]:
            layout = Layout.objects.filter(name=ret["article"]).last()
            if not layout:
                layout, _ = Layout.objects.get_or_create(
                    name=ret["article"],
                    defaults={
                        "project_id": ret["project_id"],
                        "building_id": ret["building_id"],
                        "floor_id": ret["floor_id"],
                    },
                )
            ret["layout"] = layout
        ret = self.disable_features(ret)
        return ret

    @staticmethod
    def disable_features(ret) -> dict:
        """Отключение особенностей объекта недвижимости"""

        disabled_features = Feature.objects.filter(
            property_kind__contains=[ret["type"]], lot_page_show=False
        ).values_list("kind", flat=True)

        for feature in disabled_features:
            if not feature == FeatureType.HAS_BALCONY_OR_LOGGIA:
                ret[feature] = False

        return ret

    @staticmethod
    def get_discount_prices(special_offers) -> Tuple[Optional[int], Optional[int], Optional[float]]:
        """
        Возвращает кортеж (цена, цена за кв.м, скидка),
        если есть действующие скидки
        """
        if not special_offers:
            return None, None, None
        min_price = 10**10
        min_ppm = 10**10
        value = None
        for offer in special_offers:
            temp_price, temp_ppm = offer["discount"]["calculate"].values()
            value = offer["discount"]["value"]
            if temp_price < min_price:
                min_price, min_ppm = temp_price, temp_ppm
        return min_price, min_ppm, value


class SpecialOfferProfitBaseSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    is_active = serializers.BooleanField(required=False)
    description = serializers.CharField(allow_null=True)
    descriptionActive = serializers.BooleanField(source="description_active")
    startDate = serializers.DictField()
    finishDate = serializers.DictField()
    discount = serializers.DictField()
    badge = serializers.DictField()
    propertyIds = serializers.ListField()

    class Meta:
        model = SpecialOffer
        fields = (
            "id",
            "color",
            "is_active",
            "description",
            "descriptionActive",
            "startDate",
            "finishDate",
            "discount",
            "badge",
            "propertyIds",
        )

    def to_internal_value(self, data):
        ret = super().to_internal_value(data)

        ret["properties"] = ret.pop("propertyIds")

        start: dict = ret.pop("startDate")
        finish: dict = ret.pop("finishDate")
        ret["start_date"] = parse_datetime(start.get("date"), tz=start.get("timezone"))
        ret["finish_date"] = parse_datetime(finish.get("date"), tz=finish.get("timezone"))

        badge = ret.pop("badge")
        ret["badge_icon"] = badge.get("icon")
        ret["badge_label"] = badge.get("label")

        discount: dict = ret.pop("discount")
        ret["discount_active"] = parse_bool(discount.get("active"))
        ret["is_active"] = parse_bool(discount.get("active"))
        ret["discount_value"] = parse_int(discount.get("value"))
        ret["discount_type"] = discount.get("type", "")
        ret["discount_unit"] = discount.get("unit", "")
        ret["discount_description"] = discount.get("description", "")
        return ret
