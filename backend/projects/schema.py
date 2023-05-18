"""
docs
"""

from django.db.models import Q
from django.utils import timezone
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django_optimizer import (OptimizedDjangoObjectType, query,
                                       resolver_hints)
from graphql_relay import to_global_id

from caches.decorators import cached_resolver
from common.graphene import ExtendedConnection
from common.schema import (FacetFilterField, FacetWithCountType, File,
                           MultiImageObjectTypeMeta, RangeType, SpecType)
from graphene import Boolean, Field, Int, List, Node, ObjectType, String

from .filters import GlobalProjectFilterSet, ProjectFilterSet
from .hints import project_resolve_building_set_hint
from .models import (Project, ProjectAdvantage, ProjectAdvantageSlide,
                     ProjectFeature, ProjectFeatureSlide, ProjectGallerySlide,
                     ProjectIdeology, ProjectIdeologyCard, ProjectLabel,
                     ProjectTimer, ProjectWebcam)
from .querysets import ProjectQuerySet


class ProjectFacetWithCountType(FacetWithCountType):
    """
    Тип фасетов для проекта с подсчетом недвижимости по типу
    """

    count_residential = Int()
    count_commercial = Int()
    count_current = Int()
    count_completed = Int()
    count_future = Int()


class ProjectType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип проекта
    """

    building_set = List("buildings.schema.BuildingType")
    gallery_slides = List("projects.schema.ProjectGallerySlideType")
    project_labels = List("projects.schema.ProjectLabelType")

    flat_area_range = Field(RangeType)
    parking_pantry_area_range = Field(RangeType)
    min_parking_pantry_price = Int()
    commercial_prop_area_range = Field(RangeType)
    commercial_price_range = Field(RangeType)
    commercial_area_range = Field(RangeType)
    presentation = File()

    has_parking = Boolean()
    has_commercial = Boolean()

    metro_name = String()
    global_project_id = String()

    flats_count = Int()
    parking_pantry_count = Int()
    launch_date = Int()
    commercial_count = Int()

    min_price_0 = Int()
    min_price_2 = Int()
    min_price_3 = Int()
    min_price_4 = Int()

    plan_specs_width = Int(default_value=Project.PLAN_DISPLAY_WIDTH)
    plan_specs_height = Int(default_value=Project.PLAN_DISPLAY_HEIGHT)

    traffic_map = List("properties.schema.TrafficMapType")

    class Meta:
        model = Project
        exclude = ("hash",)
        interfaces = (Node,)
        connection_class = ExtendedConnection
        convert_choices_to_enum = False
        filterset_class = ProjectFilterSet

    @classmethod
    def get_queryset(cls, queryset: 'ProjectQuerySet[Project]', info):
        if any(field in info.field_name.lower() for field in ('specs', 'facets')):
            return queryset
        qs = (queryset.select_related("metro", "city")
              .prefetch_related('trafficmap_set')
              .annotate_commercial_prices()
              .annotate_min_prop_price()
              .annotate_min_rooms_prices().annotate_flats_count()
              .annotate_parking_pantry_count().annotate_commercial_count()
              .annotate_parking_pantry_area().annotate_parking_pantry_price())
        return qs

    @classmethod
    def get_node(cls, info, _id):
        return Project.objects.get(slug=_id)

    def resolve_id(self, info):
        return getattr(self, "slug")

    @staticmethod
    @resolver_hints(prefetch_related=project_resolve_building_set_hint)
    def resolve_building_set(obj, info, **kwargs):
        return getattr(obj, "prefetched_buildings")

    @staticmethod
    def resolve_gallery_slides(obj, info, **kwargs):
        return query(ProjectGallerySlide.objects.filter(project=obj), info)

    @staticmethod
    # @resolver_hints(prefetch_related=trafficmap_set_hint)
    def resolve_traffic_map(obj, info, **kwargs):
        return obj.trafficmap_set.all()

    @staticmethod
    def resolve_project_labels(obj, info, **kwargs):
        return query(ProjectLabel.objects.filter(projects=obj).distinct(), info)

    @staticmethod
    def resolve_min_flat_price(obj, info, **kwargs):
        return getattr(obj, "min_flat_price")

    @staticmethod
    def resolve_min_commercial_prop_price(obj, info, **kwargs):
        return getattr(obj, "min_commercial_prop_price")

    @staticmethod
    def resolve_min_price_0(obj, info, **kwargs):
        """
        Результат параметра min_price_1
        :param Project obj:
        :return:
        """
        return getattr(obj, "min_price_0")

    @staticmethod
    def resolve_min_price_2(obj, info, **kwargs):
        """
        Результат параметра min_price_2
        :param Project obj:
        :return:
        """
        return getattr(obj, "min_price_2")

    @staticmethod
    def resolve_min_price_3(obj, info, **kwargs):
        """
        Результат параметра min_price_3
        :param Project obj:
        :return:
        """
        return getattr(obj, "min_price_3")

    @staticmethod
    def resolve_min_price_4(obj, info, **kwargs):
        """
        Результат параметра min_price_4
        :param Project obj:
        :return:
        """
        return getattr(obj, "min_price_4")

    @staticmethod
    def resolve_flats_count(obj, info, **kwargs):
        """
        Результат параметра flatsCount
        :param Project obj:
        :return:
        """
        return getattr(obj, "flats_count")

    @staticmethod
    def resolve_parking_pantry_count(obj, info, **kwargs):
        """
        Результат параметра parkingPantryCount
        :param Project obj:
        :return:
        """
        return getattr(obj, "parking_pantry_count")

    @staticmethod
    def resolve_commercial_count(obj, info, **kwargs):
        """
        Результат параметра commercialCount
        :param Project obj:
        :return:
        """
        return getattr(obj, "commercial_count")

    @staticmethod
    def resolve_min_parking_pantry_price(obj, info, **kwargs):
        """
        Результат параметра minParkingPantryPrice
        :param Project obj:
        :return:
        """
        return getattr(obj, "min_parking_pantry_price")

    @staticmethod
    def resolve_parking_pantry_area_range(obj, info, **kwargs):
        """
        Результат параметра parkingPantryAreaRange
        :param Project obj:
        :return:
        """
        return {"min": getattr(obj, "min_parking_area"), "max": getattr(obj, "max_parking_area")}

    @staticmethod
    def resolve_flat_area_range(obj, info, **kwargs):
        return {"min": getattr(obj, "min_flat_area"), "max": getattr(obj, "max_flat_area")}

    @staticmethod
    def resolve_commercial_prop_area_range(obj, info, **kwargs):
        return {
            "min": getattr(obj, "min_commercial_prop_area"),
            "max": getattr(obj, "max_commercial_prop_area"),
        }

    @staticmethod
    def resolve_commercial_price_range(obj, info, **kwargs):
        """
        Результат параметра commercialPriceRange
        :param Project obj:
        :return:
        """
        return {
            "min": getattr(obj, "min_commercial_price"),
            "max": getattr(obj, "max_commercial_price")
        }

    @staticmethod
    def resolve_commercial_area_range(obj, info, **kwargs):
        """
        Результат параметра commercialAreaRange
        :param Project obj:
        :return:
        """
        return {
            "min": getattr(obj, "min_parking_area"),
            "max": getattr(obj, "max_parking_area")
        }

    @staticmethod
    def resolve_metro_name(obj, info, **kwargs):
        if obj.metro:
            return obj.metro.name
        return None

    @staticmethod
    def resolve_launch_date(obj, info, **kwargs):
        if obj.launch_date:
            return obj.launch_date.year
        return None

    @staticmethod
    def resolve_global_project_id(obj, info, **kwargs):
        return to_global_id(GlobalProjectType.__name__, obj.slug)

    @staticmethod
    def resolve_timer(obj, info, **kwargs):
        """
        Результат параметра timer
        :param Project obj:
        :return:
        """
        timer = getattr(obj, "timer")
        if not timer:
            return None
        now = timezone.now()
        if not timer.end or timer.end and timer.end < now or timer.start and now < timer.start:
            return None
        return timer


class GlobalProjectType(ProjectType):
    """
    Тип глобального проекта
    """

    detail_project_id = String()

    class Meta:
        model = Project
        exclude = ("hash",)
        interfaces = (Node,)
        connection_class = ExtendedConnection
        filterset_class = GlobalProjectFilterSet

    @classmethod
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info).filter_active()

    @staticmethod
    def resolve_detail_project_id(obj, info, **kwargs):
        return to_global_id(ProjectType.__name__, obj.slug)


class ProjectGallerySlideType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип слайда галерии проекта
    """

    class Meta:
        model = ProjectGallerySlide


class ProjectLabelType(OptimizedDjangoObjectType):
    """
    Тип лейбла проекта
    """

    class Meta:
        model = ProjectLabel
        convert_choices_to_enum = False


class ProjectTimerType(OptimizedDjangoObjectType):
    """
    Тип таймера проекта
    """

    class Meta:
        model = ProjectTimer
        convert_choices_to_enum = False


class ProjectAdvantageType(OptimizedDjangoObjectType):
    """
    Тип преимущества проекта
    """

    class Meta:
        model = ProjectAdvantage


class ProjectAdvantageSlideType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип слайда преимущества проекта
    """

    class Meta:
        model = ProjectAdvantageSlide
        convert_choices_to_enum = False


class ProjectFeatureType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип особенности проекта
    """

    class Meta:
        model = ProjectFeature


class ProjectFeatureSlideType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип слайда оособенностей проекта
    """

    class Meta:
        model = ProjectFeatureSlide
        convert_choices_to_enum = False


class ProjectIdeologyType(OptimizedDjangoObjectType):
    """
    Тип идеологии проекта
    """

    class Meta:
        model = ProjectIdeology


class ProjectWebcamType(OptimizedDjangoObjectType):
    """
    Тип вебкамеры проекта
    """

    class Meta:
        model = ProjectWebcam


class ProjectIdeologyCardType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип карточки идеологии проекта
    """

    class Meta:
        model = ProjectIdeologyCard


class ProjectQuery(ObjectType):
    """
    Запросы проектов
    """

    all_projects = DjangoFilterConnectionField(
        ProjectType, exclude=String(), description="Фильтр по проектам"
    )
    all_global_projects = DjangoFilterConnectionField(
        GlobalProjectType, exclude=String(), description="Фильтр по глобальным проектам"
    )

    all_global_projects_specs = FacetFilterField(
        List(SpecType),
        filtered_type=GlobalProjectType,
        filterset_class=GlobalProjectFilterSet,
        method_name="specs",
        description="Спеки для фильтра по глобальным проектам",
    )
    all_global_projects_facets = FacetFilterField(
        ProjectFacetWithCountType,
        filtered_type=GlobalProjectType,
        filterset_class=GlobalProjectFilterSet,
        method_name="facets",
        description="Фасеты для фильтра по глобальным проектам",
    )

    project = Field(ProjectType, slug=String(), description="Получение проекта по slug")

    @staticmethod
    def resolve_all_projects(obj, info, **kwargs):
        """
        Результат запроса allProjects
        :param Any info:
        :param kwargs:
        :return:
        """
        e = Q()
        exclude = kwargs.get("exclude", None)
        if exclude:
            e &= Q(slug=exclude)
        current_site = info.context.site
        queryset = query(
            Project.objects.exclude(e)
            .filter_active()
            .filter(Q(city__site=current_site) | Q(city=None))
            .annotate_has_parking(),
            info,
        )
        return queryset

    @staticmethod
    def resolve_all_global_projects(obj, info, **kwargs):
        """
        Результат запроса allGlobalProjects
        :param Any info:
        :param kwargs:
        :return:
        """
        e = Q()
        exclude = kwargs.get("exclude", None)
        if exclude:
            e &= Q(slug=exclude)
        queryset = query(
            Project.objects.exclude(e)
            .annotate_has_parking(),
            info,
        )
        return queryset

    @staticmethod
    @cached_resolver(variables=True, user_agent=True, domain=True, crontab=False, time=5 * 60)
    def resolve_project(obj, info, **kwargs):
        """
        Кеш результат запрос project
        :param Any info:
        :param kwargs:
        :return:
        """
        qs = (Project.objects.select_related("city", "metro").filter_active()
              .annotate_commercial_prices()
              .annotate_min_prop_price()
              .annotate_min_rooms_prices()
              .annotate_flats_count()
              .annotate_parking_pantry_count()
              .annotate_commercial_count()
              .annotate_parking_pantry_area().annotate_parking_pantry_price())
        slug = kwargs.get("slug")
        if slug is not None:
            queryset = (
                query(
                    qs,
                    info,
                )
                .filter(slug=slug)
                .first()
            )
            return queryset
        return None


class ProjectWebcamQuery(ObjectType):
    """
    Запрос allProjectWebcam
    """
    all_project_webcam = List(
        ProjectWebcamType,
        slug=String(),
        description="Получение всб-камер проекта по slug или вебкамер всех проектов",
    )

    @staticmethod
    def resolve_all_project_webcam(obj, info, **kwargs):
        """
        Результат на запрос allProjectWebcam
        :param Any info:
        :param kwargs:
        :return:
        """
        slug = kwargs.get("slug")
        if slug is not None:
            return query(ProjectWebcam.objects.filter(project__slug=slug), info)
        return query(ProjectWebcam.objects.all(), info)
