from graphene import Decimal, Int, List, Node, ObjectType, String
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django_optimizer import query, resolver_hints, OptimizedDjangoObjectType
from common.schema import MultiImageObjectTypeMeta
from .filters import BuildingFilterSet, FloorFilterSet
from .models import Building, Section, Floor, GroupSection, FloorExitPlan, BuildingBookingType
from .hints import (
    floor_resolve_flat_set_hint,
    floor_resolve_commercial_set_hint,
    building_resolve_section_set_hint,
    building_resolve_residential_set_hint,
    section_resolve_floor_set_hint,
    group_section_resolve_section_set_hint,
    building_resolve_groupsection_set_hint,
    floor_exit_plan_resolve_set_hint,
)


class FloorExitPlanType(OptimizedDjangoObjectType):
    """
    Тип плана выхода с этажа
    """

    class Meta:
        model = FloorExitPlan


class FloorType(OptimizedDjangoObjectType):
    """
    Тип этажа
    """

    flat_set = List("properties.schema.GlobalFlatType")
    commercial_set = List("properties.schema.GlobalFlatType")
    floor_exit_plan_set = List(FloorExitPlanType)

    flats_count = Int()
    parking_count = Int()
    pantry_count = Int()
    commercial_count = Int()
    flats_min_price = Decimal()

    class Meta:
        model = Floor
        interfaces = (Node,)
        filterset_class = FloorFilterSet

    @staticmethod
    @resolver_hints(prefetch_related=floor_resolve_flat_set_hint)
    def resolve_flat_set(obj, info, **kwargs):
        return getattr(obj, "prefetched_flats")

    @staticmethod
    @resolver_hints(prefetch_related=floor_resolve_commercial_set_hint)
    def resolve_commercial_set(obj, info, **kwargs):
        return getattr(obj, "prefetched_commercial")

    @staticmethod
    @resolver_hints(prefetch_related=floor_exit_plan_resolve_set_hint)
    def resolve_floor_exit_plan_set(obj, info, **kwargs):
        return getattr(obj, "prefetched_floor_exit_plan")


class SectionType(OptimizedDjangoObjectType):
    """
    Тип секции
    """

    floor_set = List(FloorType)

    total_floor = Int()
    flats_count = Int()

    class Meta:
        model = Section
        interfaces = (Node,)
        filter_fields = ("id", "building")

    @staticmethod
    @resolver_hints(prefetch_related=section_resolve_floor_set_hint)
    def resolve_floor_set(obj, info, **kwargs):
        return getattr(obj, "prefetched_floors")


class SectionGroupType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип группы секции
    """

    section_set = List(SectionType)

    class Meta:
        model = GroupSection
        interfaces = (Node,)
        filter_fields = ("id", "building")

    @staticmethod
    @resolver_hints(prefetch_related=group_section_resolve_section_set_hint)
    def resolve_section_set(obj, info, **kwargs):
        return getattr(obj, "prefetched_section")


class BuildingType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип корпуса
    """

    section_set = List(SectionType)
    groupsection_set = List(SectionGroupType)
    residential_set = List("buildings.schema.BuildingType")

    days_ahead = Int()
    total_floor = Int()
    flats_count = Int()
    parking_count = Int()
    pantry_count = Int()
    commercial_count = Int()

    plan_specs_width = Int(default_value=Building.PLAN_DISPLAY_WIDTH)
    plan_specs_height = Int(default_value=Building.PLAN_DISPLAY_HEIGHT)

    class Meta:
        model = Building
        exclude = ("hash",)
        interfaces = (Node,)
        convert_choices_to_enum = False
        filterset_class = BuildingFilterSet

    @staticmethod
    @resolver_hints(prefetch_related=building_resolve_section_set_hint)
    def resolve_section_set(obj, info, **kwargs):
        return getattr(obj, "prefetched_sections")

    @staticmethod
    @resolver_hints(prefetch_related=building_resolve_residential_set_hint)
    def resolve_residential_set(obj, info, **kwargs):
        return getattr(obj, "prefetched_residential")

    @staticmethod
    @resolver_hints(prefetch_related=building_resolve_groupsection_set_hint)
    def resolve_groupsection_set(obj, info, **kwargs):
        return getattr(obj, "prefetched_groupsections")

    @staticmethod
    def resolve_days_ahead(obj, info, **kwargs):
        if obj.finish_date and obj.fact_date:
            td = obj.finish_date - obj.fact_date
            return td.days


class BuildingBookingTypeGraphene(OptimizedDjangoObjectType):
    class Meta:
        model = BuildingBookingType


class BuildingQuery(ObjectType):
    """
    Запросы корпусов
    """

    all_buildings = DjangoFilterConnectionField(BuildingType, description="Фильтр по корпусам")
    all_sections = DjangoFilterConnectionField(SectionType, description="Фильтр по секциям")
    all_floors = DjangoFilterConnectionField(FloorType, description="Фильтр про этажам")

    building = Node.Field(BuildingType, description="Получение корпуса по ID")
    section = Node.Field(SectionType, description="Получение секции по ID")
    floor = Node.Field(FloorType, description="Получение этажа по ID")

    @staticmethod
    def resolve_all_buildings(obj, info, **kwargs):
        return query(
            Building.objects.filter_active()
            .annotate_total_floor()
            .annotate_flats_count()
            .annotate_parking_count()
            .annotate_pantry_count()
            .annotate_commercial_count(),
            info,
        )

    @staticmethod
    def resolve_all_sections(obj, info, **kwargs):
        return query(Section.objects.annotate_total_floor().annotate_flats_count(), info)

    @staticmethod
    def resolve_all_floors(obj, info, **kwargs):
        return query(
            Floor.objects.annotate_flats_count()
            .annotate_flats_min_price()
            .annotate_parking_count()
            .annotate_pantry_count()
            .annotate_commercial_count(),
            info,
        )
