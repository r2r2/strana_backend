import graphene_django_optimizer as gql_optimizer
from django.contrib.sites.models import Site
from django.db.models import Prefetch, QuerySet
from graphene_django import DjangoConnectionField, DjangoObjectType
from graphene_django_optimizer import (OptimizedDjangoObjectType, query,
                                       resolver_hints)
from graphql_relay import from_global_id

import graphene
from caches.decorators import cached_resolver
from common.graphene import ExtendedConnection
from common.schema import MultiImageObjectTypeMeta
from graphene import Boolean, Field, List, Node, ObjectType, String
from projects.models import Project

from .hints import (city_resolve_hint, city_resolve_project_set_hint,
                    city_resolve_project_slides_hint)
from .models import City, Map, Metro, MetroLine, ProjectSlide, Transport
from .querysets import CityQuerySet


class SiteType(OptimizedDjangoObjectType):
    """
    Тип сайта
    """

    class Meta:
        model = Site


class CityType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип города
    """

    project_set = List("projects.schema.ProjectType")
    project_slides = List("cities.schema.ProjectPageSlideType")

    is_commercial = Boolean()
    has_commercial_page = Boolean()
    is_commercial_page_hidden = Boolean()

    has_active_projects = Boolean()

    class Meta:
        model = City
        connection_class = ExtendedConnection
        interfaces = (Node,)
        filter_fields = ()

    @classmethod
    def get_queryset(cls, queryset: 'CityQuerySet[City]', info):
        qs = queryset.prefetch_related(
            Prefetch("project_slides", queryset=ProjectSlide.objects.filter_active())
        )
        return qs

    @staticmethod
    def resolve_project_slides(obj: City, info, **kwargs):
        return obj.project_slides.all()

    @staticmethod
    @resolver_hints(prefetch_related=city_resolve_project_set_hint)
    def resolve_project_set(obj: City, info, **kwargs):
        return getattr(obj, "prefetched_projects")

    @staticmethod
    def resolve_min_commercial_price_divided(obj, info, **kwargs):
        price = getattr(obj, "min_commercial_price_divided")
        if price:
            return round(price, 2)
        return price


class ProjectPageSlideType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип слайда на главной странице
    """

    class Meta:
        model = ProjectSlide


class MetroLineType(OptimizedDjangoObjectType):
    """
    Тип линии метро
    """

    class Meta:
        model = MetroLine


class MetroType(OptimizedDjangoObjectType):
    """
    Тип метро
    """

    class Meta:
        model = Metro


class TransportType(OptimizedDjangoObjectType):
    """
    Тип транспорта
    """

    class Meta:
        model = Transport


class MapType(DjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип карты
    """

    class Meta:
        model = Map
        interfaces = (Node,)
        filter_fields = ()


class CityQuery(ObjectType):
    """
    Запросы городов
    """

    all_maps = List(MapType, description="Список карт")
    all_cities = DjangoConnectionField(CityType, description="Список городов", commercial=Boolean())

    map = Field(MapType, slug=String(), description="Получение карты по слаг")
    city = Field(CityType, id=String(), description="Город по ID")

    main_map = Field(MapType, description="Главная карта")
    current_city = Field(CityType, description="Текущий город")

    @staticmethod
    @cached_resolver(variables=True, user_agent=True, domain=True, crontab=False, time=1200)
    def resolve_all_cities(obj, info, **kwargs):
        commercial = kwargs.get("commercial", False)
        if commercial:
            queryset = gql_optimizer.query(
                City.objects.filter(active=True)
                .annotate_is_commercial()
                .filter_is_commercial()
                .annotate_has_active_projects(),
                info,
            )
            return queryset
        queryset = gql_optimizer.query(
            City.objects.filter(active=True)
            .annotate_is_commercial()
            .annotate_has_active_projects(),
            info,
        )
        return queryset

    @staticmethod
    def resolve_city(obj, info, **kwargs):
        global_id = kwargs.get("id", None)
        if global_id:
            _, id = from_global_id(global_id)
            queryset = query(
                City.objects.filter(active=True, id=id)
                .annotate_is_commercial()
                .annotate_has_active_projects(),
                info,
            ).first()
            return queryset
        return None

    @staticmethod
    def resolve_current_city(obj, info, **kwargs):
        current_site = info.context.site
        city = query(
            CityType.get_queryset(
                City.objects.all().annotate_is_commercial(),
                info,
            ).filter(site=current_site),
            info,
        )
        if city:
            return city.first()
        return None

    @staticmethod
    def resolve_all_maps(obj, info, **kwargs):
        return query(Map.objects.all(), info)

    @staticmethod
    def resolve_map(obj, info, **kwargs):
        slug = kwargs.get("slug", None)
        if slug:
            return query(Map.objects.filter(slug=slug), info).first()
        return None

    @staticmethod
    def resolve_main_map(obj, info, **kwargs):
        return query(Map.objects.filter(is_main=True), info).first()
