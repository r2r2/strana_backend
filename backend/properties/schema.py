from binascii import Error as BinasciiError

from django.db.models import OuterRef, Subquery
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django_optimizer import (OptimizedDjangoObjectType, query,
                                       resolver_hints)
from graphql_relay import from_global_id, to_global_id

from buildings.hints import commercial_space_resolve_auction_hint
from common.graphene import ExtendedConnection
from common.scalars import File
from common.schema import (FacetFilterField, FacetWithCountType,
                           MultiImageObjectTypeMeta, SpecType,
                           get_filtering_args_from_filterset)
from graphene import (ID, Boolean, Field, Float, Int, List, Mutation, Node,
                      ObjectType, String)

from .constants import FeatureType as FeatureTypeChoices
from .constants import PropertyStatus, PropertyType
from .filters import (CommercialSpaceFilterSet, FlatFilterSet,
                      FurnishFilterSet, FurnishFurnitureFilterSet,
                      FurnishKitchenFilterSet, GlobalCommercialSpaceFilterSet,
                      GlobalFlatFilterSet, GlobalPantrySpaceFilterSet,
                      GlobalParkingPantrySpaceFilterSet,
                      GlobalParkingSpaceFilterSet, LayoutFilterSet,
                      ListingActionFilterSet, PantrySpaceFilterSet,
                      ParkingPantrySpaceFilterSet, ParkingSpaceFilterSet,
                      SimilarPropertyFilterSet, UniquePlanFilterSet)
from .hints import flat_resolve_special_offer_set_hint
from .models import *
from .tasks import update_layout_min_mortgage_task
from .utils import internal_access


class TrafficMapType(OptimizedDjangoObjectType):
    """Тип Объект собственности на карте"""

    class Meta:
        model = TrafficMap


class FeatureType(OptimizedDjangoObjectType):
    """Тип особенности объекта собственности"""

    icon = File()

    class Meta:
        model = Feature


class WindowViewAngleObjectType(OptimizedDjangoObjectType):
    """Тип угла обзора"""

    class Meta:
        model = WindowViewAngle
        exclude = ("window_view",)


class WindowViewTypeObjectType(OptimizedDjangoObjectType):
    """Тип типа вида из окна"""

    class Meta:
        model = WindowViewType


class WindowViewObjectType(OptimizedDjangoObjectType):
    """Тип вида из окна"""

    class Meta:
        model = WindowView


class MiniPlanPointType(OptimizedDjangoObjectType):
    """Топ точки на мини-плане"""

    class Meta:
        model = MiniPlanPoint


class MiniPlanPointAngleType(OptimizedDjangoObjectType):
    """Топ угла точки на мини-плане"""

    class Meta:
        model = MiniPlanPointAngle
        exclude = ("mini_plan",)


class SimilarPropertySpecsType(ObjectType):
    """
    Тип похожих объектов собственности
    """

    label = String()
    value = String()


class FilteredFurnishType(OptimizedDjangoObjectType):
    """
    Тип отделки
    """

    class Meta:
        model = Furnish
        interfaces = (Node,)
        connection_class = ExtendedConnection
        filterset_class = FurnishFilterSet


class FilteredFurnishKitchenType(OptimizedDjangoObjectType):
    """
    Тип отделки кухни
    """

    class Meta:
        model = FurnishKitchen
        interfaces = (Node,)
        connection_class = ExtendedConnection
        filterset_class = FurnishKitchenFilterSet


class FilteredFurnishFurnitureType(OptimizedDjangoObjectType):
    """
    Тип отделки мебели
    """

    class Meta:
        model = FurnishFurniture
        interfaces = (Node,)
        connection_class = ExtendedConnection
        filterset_class = FurnishFurnitureFilterSet


class FurnishAdvantageType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип преимущества отделки
    """

    class Meta:
        model = FurnishAdvantage


class FurnishKitchenAdvantageType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип преимущества отделки кухни
    """

    class Meta:
        model = FurnishKitchenAdvantage


class FurnishFurnitureAdvantageType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип преимущества отделки мебели
    """

    class Meta:
        model = FurnishFurnitureAdvantage


class JobDescriptionType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип описания работ
    """

    class Meta:
        model = JobDescription


class JobDescriptionKitchenType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип описания работ
    """

    class Meta:
        model = JobDescriptionKitchen


class JobDescriptionFurnitureType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип описания работ
    """

    class Meta:
        model = JobDescriptionFurniture


class FurnishType(OptimizedDjangoObjectType):
    """
    Тип отделки
    """

    furnish_advantages = List(FurnishAdvantageType)
    jod_descriptions = List(JobDescriptionType)

    class Meta:
        model = Furnish

    @staticmethod
    @resolver_hints
    def resolve_furnish_advantages(obj, info, **kwargs):
        return getattr(obj, "furnishadvantage_set")

    @staticmethod
    @resolver_hints
    def resolve_jod_descriptions(obj, info, **kwargs):
        return getattr(obj, "jobdescription_set")


class FurnishKitchenType(OptimizedDjangoObjectType):
    """
    Тип отделки кухни
    """

    furnish_advantages = List(FurnishKitchenAdvantageType)
    jod_descriptions = List(JobDescriptionKitchenType)

    class Meta:
        model = FurnishKitchen

    @staticmethod
    @resolver_hints
    def resolve_furnish_advantages(obj, info, **kwargs):
        return getattr(obj, "furnishadvantage_set")

    @staticmethod
    @resolver_hints
    def resolve_jod_descriptions(obj, info, **kwargs):
        return getattr(obj, "jobdescription_set")


class FurnishFurnitureType(OptimizedDjangoObjectType):
    """
    Тип отделки мебели
    """

    furnish_advantages = List(FurnishFurnitureAdvantageType)
    jod_descriptions = List(JobDescriptionFurnitureType)

    class Meta:
        model = FurnishFurniture

    @staticmethod
    @resolver_hints
    def resolve_furnish_advantages(obj, info, **kwargs):
        return getattr(obj, "furnishadvantage_set")

    @staticmethod
    @resolver_hints
    def resolve_jod_descriptions(obj, info, **kwargs):
        return getattr(obj, "jobdescription_set")


class FurnishImageType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип изображения отделки
    """

    class Meta:
        model = FurnishImage


class FurnishPointType(OptimizedDjangoObjectType):
    """
    Тип точки на изображении отделки
    """

    class Meta:
        model = FurnishPoint


class FurnishKitchenImageType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип изображения отделки кухни
    """

    class Meta:
        model = FurnishKitchenImage


class FurnishKitchenPointType(OptimizedDjangoObjectType):
    """
    Тип точки на изображении отделки кухни
    """

    class Meta:
        model = FurnishKitchenPoint


class FurnishFurnitureImageType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип изображения отделки мебели
    """

    class Meta:
        model = FurnishFurnitureImage


class FurnishFurniturePointType(OptimizedDjangoObjectType):
    """
    Тип точки на изображении отделки мебели
    """

    class Meta:
        model = FurnishFurniturePoint


class FlatRoomsMenuType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип изображений квартир для меню
    """

    class Meta:
        model = FlatRoomsMenu


class PropertyCardType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип карточки подборщика
    """

    class Meta:
        model = PropertyCard


class ListingActionType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """Тип акции в лиситинге квартир"""

    class Meta:
        model = ListingAction
        interfaces = (Node,)
        connection_class = ExtendedConnection
        filterset_class = ListingActionFilterSet


class FurnishCategoryType(OptimizedDjangoObjectType):
    """
    Тип категории отделки
    """

    class Meta:
        model = FurnishCategory


class SpecialOfferType(OptimizedDjangoObjectType):
    """
    Тип акции объекта собственности
    """

    icon = File()

    class Meta:
        model = SpecialOffer


class PropertyConfigType(OptimizedDjangoObjectType):
    """
    Тип настроек объектов собственности
    """

    class Meta:
        model = PropertyConfig


class PropertyPurposeType(OptimizedDjangoObjectType):
    """
    Тип назначения помещения
    """

    class Meta:
        model = PropertyPurpose


class GlobalFlatFilterType(OptimizedDjangoObjectType):
    class Meta:
        model = Property
        interfaces = (Node,)
        connection_class = ExtendedConnection
        filterset_class = GlobalFlatFilterSet
        exclude = ("hash", "has_tenant")

    @classmethod
    def get_queryset(cls, queryset, info):
        queryset = (
            super()
            .get_queryset(queryset, info)
            .filter(type__in=[PropertyType.FLAT, PropertyType.COMMERCIAL_APARTMENT])
            .annotate_is_favorite(info.context.favorite.keys)
            .annotate_has_discount()
            .annotate_has_balcony_or_loggia()
        )
        if not internal_access(info):
            queryset = queryset.filter_active()
        return queryset


class GlobalFlatType(GlobalFlatFilterType):
    """
    Тип глобальной квартиры
    """

    pk = String()

    status = Int()
    completed = Boolean()
    has_discount = Boolean()
    is_favorite = Boolean()

    infra = String()
    infra_text = String()

    min_mortgage = Int()
    min_rate = Float()
    first_payment = Int()

    building_total_floor = Int()

    plan_3d = File()
    plan_3d_1 = File()
    plan_png = File()
    plan_png_preview = File()
    bank_logo_1 = File()
    bank_logo_2 = File()

    features = List(FeatureType)
    special_offers = List(SpecialOfferType)
    booking_days = Int()
    detail_url = String()

    furnish_price = Int()
    min_furnish_mortgage = Int()
    min_furnish_rate = Float()

    furnish_price_comfort = Int()
    min_furnish_comfort_mortgage = Int()
    min_furnish_comfort_rate = Float()

    furnish_price_business = Int()
    min_furnish_business_mortgage = Int()
    min_furnish_business_rate = Float()

    furnish_kitchen_price = Int()
    min_furnish_kitchen_mortgage = Int()
    min_furnish_kitchen_rate = Float()

    furnish_furniture_price = Int()
    min_furnish_furniture_mortgage = Int()
    min_furnish_furniture_rate = Float()

    furnish_kitchen_furniture_price = Int()
    min_furnish_kitchen_furniture_mortgage = Int()
    min_furnish_kitchen_furniture_rate = Float()

    class Meta:
        model = Property
        interfaces = (Node,)
        connection_class = ExtendedConnection
        filterset_class = GlobalFlatFilterSet
        exclude = ("hash", "has_tenant")

    @classmethod
    def get_queryset(cls, queryset, info):

        return (
            super()
            .get_queryset(queryset, info)
            .annotate_rooms_type()
            .annotate_completed()
            .annotate_infra()
            .annotate_first_payment()
            .annotate_building_total_floor()
            .annotate_mortgage_type()
            .annotate_min_mortgage(info.variable_values.get("deposit", 20))
            .order_plan()
            .annotate_booking_days()
            .annotate_furnish_price()
            .annotate_furnish_price_comfort()
            .annotate_furnish_price_business()
            .annotate_min_furnish_mortgage()
            .annotate_min_furnish_comfort_mortgage()
            .annotate_min_furnish_business_mortgage()
            .annotate_furnish_kitchen_price()
            .annotate_furnish_furniture_price()
            .annotate_furnish_kitchen_furniture_price()
            .annotate_min_furnish_kitchen_mortgage()
            .annotate_min_furnish_furniture_mortgage()
            .annotate_min_furnish_kitchen_furniture_mortgage()
        )

    @staticmethod
    def resolve_detail_url(obj, info, **kwargs):
        return f"https://{info.context.site.domain}/{obj.project.slug}/flats/"

    @staticmethod
    def resolve_is_favorite(obj, info, **kwargs):
        return getattr(obj, "is_favorite", False)

    @staticmethod
    def resolve_features(obj, info, **kwargs):
        kinds = []
        for kind in FeatureTypeChoices.values:
            if getattr(obj, kind, False):
                kinds.append(kind)
        return query(Feature.objects.filter(property_kind=[obj.type],
                                            kind__in=kinds, lot_page_show=True), info)

    @staticmethod
    @resolver_hints(prefetch_related=flat_resolve_special_offer_set_hint)
    def resolve_special_offers(obj, info, **kwargs):
        return getattr(obj, "prefetched_specialoffer_set")


class FlatType(GlobalFlatType):
    """
    Тип квартиры
    """

    pk = String()

    class Meta:
        model = Property
        interfaces = (Node,)
        connection_class = ExtendedConnection
        filterset_class = FlatFilterSet
        exclude = ("hash", "has_tenant")

    @classmethod
    def get_queryset(cls, queryset, info):
        current_site = info.context.site
        return super().get_queryset(queryset, info).filter_current_site(current_site)


class GlobalParkingSpaceType(OptimizedDjangoObjectType):
    """
    Тип глобального парковочного места
    """

    pk = String()

    status = Int()
    is_favorite = Boolean()

    class Meta:
        model = Property
        interfaces = (Node,)
        connection_class = ExtendedConnection
        filterset_class = GlobalParkingSpaceFilterSet
        exclude = (
            "hash",
            "rooms",
            "is_apartments",
            "is_penthouse",
            "open_plan",
            "facing",
            "has_view",
            "living_area",
            "kitchen_area",
            "bedrooms_count",
            "loggias_count",
            "balconies_count",
            "stores_count",
            "wardrobes_count",
            "separate_wcs_count",
            "combined_wcs_count",
            "furnish_set",
            "furnish_kitchen_set",
            "furnish_furniture_set",
            "has_parking",
            "has_terrace",
            "is_duplex",
            "has_high_ceiling",
            "has_panoramic_windows",
            "has_two_sides_windows",
            "has_tenant",
        )

    @classmethod
    def get_queryset(cls, queryset, info):
        if internal_access(info):
            return (
                super()
                .get_queryset(queryset, info)
                .annotate_has_discount()
                .annotate_is_favorite(info.context.favorite.keys)
            )
        return (
            super()
            .get_queryset(queryset, info)
            .filter(type=PropertyType.PARKING)
            .filter_active(include_booked=False)
            .annotate_has_discount()
            .annotate_is_favorite(info.context.favorite.keys)
            .filter_enabled_parkings()
        )

    @staticmethod
    def resolve_is_favorite(obj, info, **kwargs):
        return getattr(obj, "is_favorite", False)


class ParkingSpaceType(GlobalParkingSpaceType):
    """
    Тип парковочного места
    """

    pk = String()

    class Meta:
        model = Property
        interfaces = (Node,)
        connection_class = ExtendedConnection
        filterset_class = ParkingSpaceFilterSet
        exclude = (
            "hash",
            "rooms",
            "is_apartments",
            "is_penthouse",
            "open_plan",
            "facing",
            "has_view",
            "living_area",
            "kitchen_area",
            "bedrooms_count",
            "loggias_count",
            "balconies_count",
            "stores_count",
            "wardrobes_count",
            "separate_wcs_count",
            "combined_wcs_count",
            "furnish_set",
            "furnish_kitchen_set",
            "furnish_furniture_set",
            "has_parking",
            "has_terrace",
            "is_duplex",
            "has_high_ceiling",
            "has_panoramic_windows",
            "has_two_sides_windows",
            "has_tenant",
        )

    @classmethod
    def get_queryset(cls, queryset, info):
        current_site = info.context.site
        return super().get_queryset(queryset, info).filter_current_site(current_site)


class GlobalPantrySpaceType(OptimizedDjangoObjectType):
    """
    Тип глобального парковочного места
    """

    pk = String()

    status = Int()
    is_favorite = Boolean()

    class Meta:
        model = Property
        interfaces = (Node,)
        connection_class = ExtendedConnection
        filterset_class = GlobalPantrySpaceFilterSet
        exclude = (
            "hash",
            "rooms",
            "is_apartments",
            "is_penthouse",
            "open_plan",
            "facing",
            "has_view",
            "living_area",
            "kitchen_area",
            "bedrooms_count",
            "loggias_count",
            "balconies_count",
            "stores_count",
            "wardrobes_count",
            "separate_wcs_count",
            "combined_wcs_count",
            "furnish_set",
            "furnish_kitchen_set",
            "furnish_furniture_set",
            "has_parking",
            "has_terrace",
            "is_duplex",
            "has_high_ceiling",
            "has_panoramic_windows",
            "has_two_sides_windows",
            "has_tenant",
        )

    @classmethod
    def get_queryset(cls, queryset, info):
        if internal_access(info):
            return (
                super()
                    .get_queryset(queryset, info)
                    .annotate_has_discount()
                    .annotate_is_favorite(info.context.favorite.keys)
            )
        return (
            super()
                .get_queryset(queryset, info)
                .filter(type=PropertyType.PANTRY)
                .annotate_is_favorite(info.context.favorite.keys)
                .annotate_has_discount()
                .filter_active(include_booked=False)
        )

    @staticmethod
    def resolve_is_favorite(obj, info, **kwargs):
        return getattr(obj, "is_favorite", False)


class GlobalParkingPantrySpaceType(OptimizedDjangoObjectType):
    """
    Тип глобального парковочного места и кладовых
    """

    pk = String()

    status = Int()
    is_favorite = Boolean()

    class Meta:
        model = Property
        interfaces = (Node,)
        connection_class = ExtendedConnection
        filterset_class = GlobalParkingPantrySpaceFilterSet
        exclude = (
            "hash",
            "rooms",
            "is_apartments",
            "is_penthouse",
            "open_plan",
            "facing",
            "has_view",
            "living_area",
            "kitchen_area",
            "bedrooms_count",
            "loggias_count",
            "balconies_count",
            "stores_count",
            "wardrobes_count",
            "separate_wcs_count",
            "combined_wcs_count",
            "furnish_set",
            "furnish_kitchen_set",
            "furnish_furniture_set",
            "has_parking",
            "has_terrace",
            "is_duplex",
            "has_high_ceiling",
            "has_panoramic_windows",
            "has_two_sides_windows",
            "has_tenant",
        )

    @classmethod
    def get_queryset(cls, queryset, info):
        if internal_access(info):
            return (
                super()
                    .get_queryset(queryset, info)
                    .annotate_has_discount()
                    .annotate_is_favorite(info.context.favorite.keys)
            )
        return (
            super()
                .get_queryset(queryset, info)
                .filter(type__in=[PropertyType.PARKING, PropertyType.PANTRY])
                .annotate_is_favorite(info.context.favorite.keys)
                .annotate_has_discount()
                .filter_active(include_booked=False)
                .filter_enabled_parkings()
        )

    @staticmethod
    def resolve_is_favorite(obj, info, **kwargs):
        return getattr(obj, "is_favorite", False)


class PantrySpaceType(GlobalPantrySpaceType):
    """
    Тип кладовочного места
    """

    pk = String()

    class Meta:
        model = Property
        interfaces = (Node,)
        connection_class = ExtendedConnection
        filterset_class = PantrySpaceFilterSet
        exclude = (
            "hash",
            "rooms",
            "is_apartments",
            "is_penthouse",
            "open_plan",
            "facing",
            "has_view",
            "living_area",
            "kitchen_area",
            "bedrooms_count",
            "loggias_count",
            "balconies_count",
            "stores_count",
            "wardrobes_count",
            "separate_wcs_count",
            "combined_wcs_count",
            "furnish_set",
            "furnish_kitchen_set",
            "furnish_furniture_set",
            "has_parking",
            "has_terrace",
            "is_duplex",
            "has_high_ceiling",
            "has_panoramic_windows",
            "has_two_sides_windows",
            "has_tenant",
        )

    @classmethod
    def get_queryset(cls, queryset, info):
        current_site = info.context.site
        return super().get_queryset(queryset, info).filter_current_site(current_site)


class ParkingPantrySpaceType(GlobalParkingPantrySpaceType):
    """
    Тип паркинга и кладовочного места
    """

    pk = String()

    class Meta:
        model = Property
        interfaces = (Node,)
        connection_class = ExtendedConnection
        filterset_class = ParkingPantrySpaceFilterSet
        exclude = (
            "hash",
            "rooms",
            "is_apartments",
            "is_penthouse",
            "open_plan",
            "facing",
            "has_view",
            "living_area",
            "kitchen_area",
            "bedrooms_count",
            "loggias_count",
            "balconies_count",
            "stores_count",
            "wardrobes_count",
            "separate_wcs_count",
            "combined_wcs_count",
            "furnish_set",
            "furnish_kitchen_set",
            "furnish_furniture_set",
            "has_parking",
            "has_terrace",
            "is_duplex",
            "has_high_ceiling",
            "has_panoramic_windows",
            "has_two_sides_windows",
            "has_tenant",
        )

    @classmethod
    def get_queryset(cls, queryset, info):
        current_site = info.context.site
        return super().get_queryset(queryset, info).filter_current_site(current_site)


class GlobalCommercialSpaceType(OptimizedDjangoObjectType):
    """
    Тип глобального коммерческого помещения
    """

    pk = String()

    min_mortgage = Int()
    building_total_floor = Int()

    is_favorite = Boolean()
    has_auction = Boolean()

    bank_logo_1 = File()
    bank_logo_2 = File()

    features = List(FeatureType)
    auction = Field("auction.schema.AuctionType")
    furnish_set = List("properties.schema.FurnishType")
    furnish_kitchen_set = List("properties.schema.FurnishKitchenType")
    furnish_furniture_set = List("properties.schema.FurnishFurnitureType")


    class Meta:
        model = Property
        interfaces = (Node,)
        connection_class = ExtendedConnection
        filterset_class = GlobalCommercialSpaceFilterSet
        exclude = (
            "hash",
            "rooms",
            "is_apartments",
            "is_penthouse",
            "open_plan",
            "facing",
            "has_view",
            "living_area",
            "kitchen_area",
            "bedrooms_count",
            "loggias_count",
            "balconies_count",
            "stores_count",
            "wardrobes_count",
            "separate_wcs_count",
            "combined_wcs_count",
            "has_parking",
            "has_terrace",
            #"is_duplex",
            #"has_high_ceiling",
            #"has_panoramic_windows",
            #"has_two_sides_windows",
        )

    @classmethod
    def get_queryset(cls, queryset, info):
        if internal_access(info):
            return (
                super()
                .get_queryset(queryset, info)
                .filter(type__in=[PropertyType.COMMERCIAL, PropertyType.COMMERCIAL_APARTMENT])
                .annotate_has_discount()
                .annotate_is_favorite(info.context.favorite.keys)
                .annotate_completed()
                .annotate_mortgage_type()
                .annotate_min_mortgage()
                .annotate_building_total_floor()
            )
        return (
            super()
            .get_queryset(queryset, info)
            .filter(type__in=[PropertyType.COMMERCIAL, PropertyType.COMMERCIAL_APARTMENT])
            .filter_active()
            .annotate_has_discount()
            .annotate_has_auction()
            .annotate_is_favorite(info.context.favorite.keys)
            .annotate_completed()
            .annotate_mortgage_type()
            .annotate_min_mortgage()
            .annotate_building_total_floor()
        )

    @staticmethod
    def resolve_is_favorite(obj, info, **kwargs):
        return getattr(obj, "is_favorite", False)

    @staticmethod
    @resolver_hints(select_related=("project", "project__city"))
    def resolve_furnish_set(obj, info, **kwargs):
        city = obj.project.city if hasattr(obj.project, "city") else info.context.site.city
        return query(Furnish.objects.filter(commercialpropertypage__city=city).distinct(), info)

    @staticmethod
    @resolver_hints(select_related=("project", "project__city"))
    def resolve_furnish_kitchen_set(obj, info, **kwargs):
        city = obj.project.city if hasattr(obj.project, "city") else info.context.site.city
        return query(FurnishKitchen.objects.filter(commercialpropertypage__city=city).distinct(), info)

    @staticmethod
    @resolver_hints(select_related=("project", "project__city"))
    def resolve_furnish_furniture_set(obj, info, **kwargs):
        city = obj.project.city if hasattr(obj.project, "city") else info.context.site.city
        return query(FurnishFurniture.objects.filter(commercialpropertypage__city=city).distinct(), info)

    @staticmethod
    @resolver_hints(prefetch_related=commercial_space_resolve_auction_hint)
    def resolve_auction(obj, info, **kwargs):
        auction = getattr(obj, "prefetched_auction_set")
        if auction:
            return auction[0]

    @staticmethod
    def resolve_features(obj, info, **kwargs):
        kinds = []
        for kind in FeatureTypeChoices.values:
            if getattr(obj, kind, False):
                kinds.append(kind)
        return query(Feature.objects.filter(kind__in=kinds, icon_flats_show=True), info)


class CommercialSpaceType(GlobalCommercialSpaceType):
    """
    Тип коммерческого помещения
    """

    pk = String()

    class Meta:
        model = Property
        interfaces = (Node,)
        connection_class = ExtendedConnection
        filterset_class = CommercialSpaceFilterSet
        exclude = (
            "hash",
            "rooms",
            "is_apartments",
            "is_penthouse",
            "open_plan",
            "facing",
            "has_view",
            "living_area",
            "kitchen_area",
            "bedrooms_count",
            "loggias_count",
            "balconies_count",
            "stores_count",
            "wardrobes_count",
            "separate_wcs_count",
            "combined_wcs_count",
            "has_parking",
            "has_terrace",
            "is_duplex",
            "has_high_ceiling",
            "has_panoramic_windows",
            "has_two_sides_windows",
        )

    @classmethod
    def get_queryset(cls, queryset, info):
        current_site = info.context.site
        return super().get_queryset(queryset, info).filter_current_site(current_site)


class UniquePlanType(OptimizedDjangoObjectType):
    """
    Тип уникальной планировки
    """

    is_favorite = Boolean()

    class Meta:
        model = Property
        interfaces = (Node,)
        connection_class = ExtendedConnection
        filterset_class = UniquePlanFilterSet
        exclude = ("hash", "has_tenant")

    @classmethod
    def get_queryset(cls, queryset, info):
        return (
            super()
            .get_queryset(queryset, info)
            .filter_active()
            .filter(type=PropertyType.FLAT)
            .order_by("plan_code", "price")
            .distinct("plan_code")
        )

    @staticmethod
    def resolve_is_favorite(obj, info, **kwargs):
        return getattr(obj, "is_favorite", False)


class ChangePropertyStatusMutation(Mutation):
    """
    Изменение статуса объекта недвижимости
    """

    class Arguments:
        id = ID(required=True)
        status = String(required=True)

    ok = Boolean()
    reason = String()

    @staticmethod
    def mutate(obj, info, **kwargs):
        if not internal_access(info):
            return ChangePropertyStatusMutation(ok=False, reason="denied")
        global_id = kwargs.get("id")
        status = kwargs.get("status")
        _, id = from_global_id(global_id)
        property = Property.objects.filter(id=id).first()
        if not property:
            return ChangePropertyStatusMutation(ok=False, reason="no_property")
        property.status = status

        property.save()
        if status == PropertyStatus.FREE:
            layout = Layout.objects.filter(property=property)
            if layout.id:
                update_layout_min_mortgage_task.delay(layout.id)
        return ChangePropertyStatusMutation(ok=True, reason="success")


class ChangePropertyMutation(Mutation):
    """
    Изменение данных объекта недвижимости
    """

    class Arguments:
        id = ID(required=True)
        has_viewed = Boolean(required=False)

    ok = Boolean()

    @classmethod
    def mutate(cls, obj, info, **kwargs):
        global_id = kwargs.get("id")
        has_viewed = kwargs.get("has_viewed")
        try:
            _, _id = from_global_id(global_id)
        except (UnicodeDecodeError, BinasciiError, ValueError):
            return cls(ok=False)
        property = Property.objects.filter(id=_id).first()
        if not property:
            return cls(ok=False)

        if has_viewed:
            property.views_count += 1
        property.save()
        return cls(ok=True)


class PropertyCommercialGalleryType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип гелиреи для коммерческих объектов собственности
    """

    class Meta:
        model = PropertyCommercialGallery
        exclude = ("property",)


class LayoutObjectType(OptimizedDjangoObjectType):
    """Тип планировки"""

    plan = File()
    planoplan = File()
    floor_plan = File()

    price = Int()
    original_price = Int()
    max_discount = Int()
    first_payment = Int()
    completion_date = String()
    first_flat_url = String()
    flat_id = String()
    plan_hover = String()
    has_special_offers = Boolean()
    has_badge = Boolean()
    features = List(FeatureType)

    class Meta:
        model = Layout
        interfaces = (Node,)
        connection_class = ExtendedConnection
        filterset_class = LayoutFilterSet
        convert_choices_to_enum = False

    @classmethod
    def get_queryset(cls, queryset, info, flat_qs = None):
        qs = super().get_queryset(queryset, info)
        params = {
            'price__gte': info.variable_values.get('priceMin'),
            'price__lte': info.variable_values.get('priceMax'),
            'area__gte': info.variable_values.get('areaMin'),
            'area__lte': info.variable_values.get('areaMax'),
            'floor__number__gte': info.variable_values.get('floorMin'),
            'floor__number__lte': info.variable_values.get('floorMax'),
        }
        params = {k: v for k, v in params.items() if v is not None}
        qs = (qs.annotate_property_stats(flat_qs, params)
                .annotate_has_badge()
                .annotate_has_special_offers()
                .annotate_first_payment()
                .annotate_mortgage_type()
                .distinct())
        return qs

    @staticmethod
    def resolve_features(obj, info, **kwargs):
        kinds = []
        for kind in FeatureTypeChoices.values:
            if getattr(obj, kind, False):
                kinds.append(kind)
        return query(Feature.objects.filter(kind__in=kinds, icon_flats_show=True), info)

    @staticmethod
    @resolver_hints(select_related="project")
    def resolve_first_flat_url(obj, info, **kwargs):
        if not obj.first_flat_id or not obj.project:
            return
        flat_id = to_global_id(GlobalFlatType.__name__, obj.first_flat_id)
        return f"https://{info.context.site.domain}/{obj.project.slug}/flats/{flat_id}/"

    @staticmethod
    @resolver_hints(select_related="project")
    def resolve_flat_id(obj, info, **kwargs):
        if not obj.first_flat_id or not obj.project:
            return
        flat_id = to_global_id(GlobalFlatType.__name__, obj.first_flat_id)
        return f"{flat_id}"


class FlatFacetsType(FacetWithCountType):
    with_commercial = Boolean()
    with_flat = Boolean()
    with_commercial_apartment = Boolean()


class PropertyQuery(ObjectType):
    """
    Запросы объектов собственности
    """

    all_global_flats = DjangoFilterConnectionField(
        GlobalFlatType, description="Фильтр по квартирам без домена"
    )
    all_global_parking_pantry_spaces = DjangoFilterConnectionField(
        GlobalParkingPantrySpaceType, description="Фильтр по парковочным и кладовым местам без домена"
    )
    all_global_parking_spaces = DjangoFilterConnectionField(
        GlobalParkingSpaceType, description="Фильтр по парковочным местам без домена"
    )
    all_global_pantry_spaces = DjangoFilterConnectionField(
        GlobalPantrySpaceType, description="Фильтр по кладовым местам без домена"
    )
    all_global_commercial_spaces = DjangoFilterConnectionField(
        GlobalCommercialSpaceType, description="Фильтр по коммерческим помещениям без домена"
    )

    all_flats = DjangoFilterConnectionField(FlatType, description="Фильтр по квартирам")
    all_parking_spaces = DjangoFilterConnectionField(
        ParkingSpaceType, description="Фильтр по парковочным местам"
    )
    all_pantry_spaces = DjangoFilterConnectionField(
        PantrySpaceType, description="Фильтр по кладовым местам"
    )
    all_parking_pantry_spaces = DjangoFilterConnectionField(
        ParkingPantrySpaceType, description="Фильтр по парковочным местам и кладовым"
    )
    all_commercial_spaces = DjangoFilterConnectionField(
        CommercialSpaceType, description="Фильтр по коммерческим помещениям"
    )
    all_unique_plans = DjangoFilterConnectionField(
        UniquePlanType, description="Все уникальные планировки"
    )
    all_property_cards = List(PropertyCardType, description="Карточки для подборщика")
    similar_flats = DjangoFilterConnectionField(
        GlobalFlatType,
        id=ID(required=True),
        filterset_class=SimilarPropertyFilterSet,
        description="Фильтр похожих квартир",
    )
    all_furnishes = DjangoFilterConnectionField(
        FilteredFurnishType, description="Фильтр по отделкам"
    )

    all_furnishes_kitchen = DjangoFilterConnectionField(
        FilteredFurnishKitchenType, description="Фильтр по отделкам кухни"
    )

    all_furnishes_furniture = DjangoFilterConnectionField(
        FilteredFurnishFurnitureType, description="Фильтр по отделкам мебели"
    )

    similar_commercial_spaces = DjangoFilterConnectionField(
        GlobalCommercialSpaceType,
        id=ID(required=True),
        filterset_class=SimilarPropertyFilterSet,
        description="Фильтр похожих коммерческих помещений",
    )

    all_global_flats_facets = FacetFilterField(
        FlatFacetsType,
        filtered_type=GlobalFlatFilterType,
        filterset_class=GlobalFlatFilterSet,
        method_name="facets",
        description="Фасеты для фильтра по квартирам без домена",
    )
    all_global_flats_specs = FacetFilterField(
        List(SpecType),
        filtered_type=GlobalFlatFilterType,
        filterset_class=GlobalFlatFilterSet,
        method_name="specs",
        description="Спеки для фильтра по квартирам без домена",
    )
    all_global_parking_spaces_facets = FacetFilterField(
        FacetWithCountType,
        filtered_type=GlobalParkingSpaceType,
        filterset_class=GlobalParkingSpaceFilterSet,
        method_name="facets",
        description="Фасеты для фильтра по парковочным местам без домена",
    )
    all_global_pantry_spaces_facets = FacetFilterField(
        FacetWithCountType,
        filtered_type=GlobalPantrySpaceType,
        filterset_class=GlobalPantrySpaceFilterSet,
        method_name="facets",
        description="Фасеты для фильтра по кладовым местам без домена",
    )

    all_global_parking_spaces_specs = FacetFilterField(
        List(SpecType),
        filtered_type=GlobalParkingSpaceType,
        filterset_class=GlobalParkingSpaceFilterSet,
        method_name="specs",
        description="Спеки для фильтра по парковочным местам без домена",
    )

    all_global_parking_pantry_spaces_facets = FacetFilterField(
        FacetWithCountType,
        filtered_type=GlobalParkingPantrySpaceType,
        filterset_class=GlobalParkingPantrySpaceFilterSet,
        method_name="facets",
        description="Фасеты для фильтра по кладовым местам и парковкам без домена",
    )

    all_global_parking_pantry_spaces_specs = FacetFilterField(
        List(SpecType),
        filtered_type=GlobalParkingPantrySpaceType,
        filterset_class=GlobalParkingPantrySpaceFilterSet,
        method_name="specs",
        description="Спеки для фильтра по парковочным местам и кладовым без домена",
    )

    all_global_commercial_spaces_facets = FacetFilterField(
        FacetWithCountType,
        filtered_type=GlobalCommercialSpaceType,
        filterset_class=GlobalCommercialSpaceFilterSet,
        method_name="facets",
        description="Фасеты для фильтра по коммерческим помещениям без домена",
    )
    all_global_commercial_spaces_specs = FacetFilterField(
        List(SpecType),
        filtered_type=GlobalCommercialSpaceType,
        filterset_class=GlobalCommercialSpaceFilterSet,
        method_name="specs",
        description="Спеки для фильтра по коммерческим помещениям без домена",
    )
    all_listing_actions = DjangoFilterConnectionField(
        ListingActionType, description="Получение акций для фильтра квартир"
    )

    all_flats_facets = FacetFilterField(
        FlatFacetsType,
        filtered_type=FlatType,
        filterset_class=FlatFilterSet,
        method_name="facets",
        description="Фасеты для фильтра по квартирам",
    )
    all_flats_specs = FacetFilterField(
        List(SpecType),
        filtered_type=FlatType,
        filterset_class=FlatFilterSet,
        method_name="specs",
        description="Спеки для фильтра по квартирам",
    )
    all_parking_spaces_facets = FacetFilterField(
        FacetWithCountType,
        filtered_type=ParkingSpaceType,
        filterset_class=ParkingSpaceFilterSet,
        method_name="facets",
        description="Фасеты для фильтра по парковочным местам",
    )
    all_parking_spaces_specs = FacetFilterField(
        List(SpecType),
        filtered_type=ParkingSpaceType,
        filterset_class=ParkingSpaceFilterSet,
        method_name="specs",
        description="Спеки для фильтра по парковочным местам",
    )
    all_commercial_spaces_facets = FacetFilterField(
        FacetWithCountType,
        filtered_type=CommercialSpaceType,
        filterset_class=CommercialSpaceFilterSet,
        method_name="facets",
        description="Фасеты для фильтра по коммерческим помещениям",
    )
    all_commercial_spaces_specs = FacetFilterField(
        List(SpecType),
        filtered_type=CommercialSpaceType,
        filterset_class=CommercialSpaceFilterSet,
        method_name="specs",
        description="Спеки для фильтра по коммерческим помещениям",
    )

    all_unique_plans_specs = FacetFilterField(
        List(SpecType),
        filtered_type=UniquePlanType,
        filterset_class=UniquePlanFilterSet,
        method_name="specs",
        description="Спеки уникальных планировок",
    )
    all_unique_plans_facets = FacetFilterField(
        FacetWithCountType,
        filtered_type=UniquePlanType,
        filterset_class=UniquePlanFilterSet,
        method_name="facets",
        description="Фасеты уникальных планировок",
    )
    similar_flats_specs = List(
        SimilarPropertySpecsType,
        id=ID(required=True),
        description="Спеки для фильтра по похожим квартирам",
    )
    similar_commercial_spaces_specs = List(
        SimilarPropertySpecsType,
        id=ID(required=True),
        description="Спеки для фильтра по похожим коммерческим помещениям",
    )
    all_layouts = DjangoFilterConnectionField(
        LayoutObjectType,
        description="Фильтр по планировкам",
        **get_filtering_args_from_filterset(GlobalFlatFilterSet, DjangoFilterConnectionField.type),
    )

    global_flat = Field(
        GlobalFlatType, id=ID(required=True), description="Получение квартиры по ID без домена"
    )
    global_commercial_space = Field(
        GlobalCommercialSpaceType,
        id=ID(required=True),
        description="Получение коммерческого помещения по ID без домена",
    )
    flat = Node.Field(FlatType, description="Получение квартиры по ID")
    commercial_space = Node.Field(
        CommercialSpaceType, description="Получение коммерческого помещения по ID"
    )
    unique_plan = Node.Field(UniquePlanType, description="Получение уникальной планировки по ID")
    layout = Field(LayoutObjectType, id=ID(required=True), description="Получение планировки по ID")
    global_parking = Field(
        GlobalParkingSpaceType,
        id=ID(required=True),
        description="Получение паркинга по ID без домена",
    )
    property_config = Field(
        PropertyConfigType, description="Получение настроект объектов собственности"
    )

    @staticmethod
    def resolve_all_global_flats(obj, info, **kwargs):
        return query(GlobalFlatType.get_queryset(Property.objects.all(), info), info)

    @staticmethod
    def resolve_all_global_parking_spaces(obj, info, **kwargs):
        return query(GlobalParkingSpaceType.get_queryset(Property.objects.all(), info), info)

    @staticmethod
    def resolve_all_global_commercial_spaces(obj, info, **kwargs):
        return query(GlobalCommercialSpaceType.get_queryset(Property.objects.all(), info), info)

    @staticmethod
    def resolve_all_flats(obj, info, **kwargs):
        return query(FlatType.get_queryset(Property.objects.all(), info), info)

    @staticmethod
    def resolve_all_parking_spaces(obj, info, **kwargs):
        return query(ParkingSpaceType.get_queryset(Property.objects.all(), info), info)

    @staticmethod
    def resolve_all_commercial_spaces(obj, info, **kwargs):
        return query(CommercialSpaceType.get_queryset(Property.objects.all(), info), info)

    @staticmethod
    def resolve_all_unique_plans(obj, info, **kwargs):
        return query(UniquePlanType.get_queryset(Property.objects.all(), info), info)

    @staticmethod
    def resolve_all_property_cards(obj, info, **kwargs):
        return query(PropertyCard.objects.all(), info)

    @staticmethod
    def resolve_all_furnishes(obj, info, **kwargs):
        return query(Furnish.objects.all(), info)

    @staticmethod
    def resolve_similar_flats(obj, info, id, **kwargs):
        try:
            _, _id = from_global_id(id)
            flat = Property.objects.filter_active().get(id=_id)
            return query(
                GlobalFlatType.get_queryset(
                    Property.objects.all().filter_active().filter_similar_flats(flat), info
                ),
                info,
            )
        except (Property.DoesNotExist, ValueError):
            return Property.objects.none()

    @staticmethod
    def resolve_similar_commercial_spaces(obj, info, id, **kwargs):
        try:
            _, _id = from_global_id(id)
            commercial_space = Property.objects.filter_active().get(id=_id)
            return query(
                GlobalCommercialSpaceType.get_queryset(
                    Property.objects.all()
                    .filter_active()
                    .filter_similar_commercial_spaces(commercial_space),
                    info,
                ),
                info,
            )
        except (Property.DoesNotExist, ValueError):
            return Property.objects.none()

    @staticmethod
    def resolve_similar_flats_specs(obj, info, **kwargs):
        id = kwargs.get("id")
        _, exclude = from_global_id(id)
        flat = Property.objects.filter_active().filter(id=exclude).first()
        if flat:
            queryset = GlobalFlatType.get_queryset(
                Property.objects.all().filter_active().filter_similar_flats(flat), info
            )
            if queryset:
                specs = SimilarPropertyFilterSet.get_tab_specs(queryset)
                return specs
            return []
        return []

    @staticmethod
    def resolve_similar_commercial_spaces_specs(obj, info, **kwargs):
        id = kwargs.get("id")
        _, exclude = from_global_id(id)
        commercial_space = Property.objects.filter_active().filter(id=exclude).first()
        if commercial_space:
            queryset = GlobalCommercialSpaceType.get_queryset(
                Property.objects.all()
                .filter_active()
                .filter_similar_commercial_spaces(commercial_space),
                info,
            )
            if queryset:
                specs = SimilarPropertyFilterSet.get_tab_specs(queryset)
                return specs
            return []
        return []

    @staticmethod
    def resolve_global_flat(obj, info, **kwargs):
        id = kwargs.get("id", None)
        if id:
            _, id = from_global_id(id)
            return (
                query(GlobalFlatType.get_queryset(Property.objects.all(), info), info)
                .filter(id=id)
                .first()
            )
        return None

    @staticmethod
    def resolve_layout(obj, info, **kwargs):
        _id = kwargs.get("id")
        if _id:
            _, _id = from_global_id(_id)
            return (
                query(LayoutObjectType.get_queryset(Layout.objects.all(), info), info)
                .filter(id=_id)
                .first()
            )

    @staticmethod
    def resolve_all_layouts(obj, info, **kwargs):
        flat_qs = query(GlobalFlatFilterType.get_queryset(Property.objects.all(), info), info)
        flat_qs = GlobalFlatFilterSet(kwargs, flat_qs).qs
        return query(
            LayoutObjectType.get_queryset(
                Layout.objects.filter(property__in=Subquery(flat_qs.values("pk"))), info, flat_qs
            ),
            info,
        )

    @staticmethod
    def resolve_global_parking(obj, info, **kwargs):
        id = kwargs.get("id", None)
        if id:
            _, id = from_global_id(id)
            return (
                query(GlobalParkingSpaceType.get_queryset(Property.objects.all(), info), info)
                .filter(id=id)
                .first()
            )
        return None

    @staticmethod
    def resolve_global_commercial_space(obj, info, **kwargs):
        id = kwargs.get("id", None)
        if id:
            _, id = from_global_id(id)
            return (
                query(GlobalCommercialSpaceType.get_queryset(Property.objects.all(), info), info)
                .filter(id=id)
                .first()
            )

    @staticmethod
    def resolve_property_config(obj, info, **kwargs):
        return PropertyConfig.get_solo()

    @staticmethod
    def resolve_all_listing_actions(obj, info, **kwargs):
        return query(ListingAction.objects.all(), info)


class PropertyMutation(ObjectType):
    """
    Мутации объектов недвижимости
    """

    change_property = ChangePropertyMutation.Field(description="Изменение объекта недвижимости")
    change_property_status = ChangePropertyStatusMutation.Field(
        description="Изменение статуса объекта недвижимости"
    )
