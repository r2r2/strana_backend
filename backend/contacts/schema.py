from graphene import ObjectType, Node, List
from graphene_django_optimizer import OptimizedDjangoObjectType, query
from graphene_django import DjangoListField
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django_optimizer import resolver_hints
from common.graphene import ExtendedConnection
from common.schema import (
    FacetFilterField,
    SpecType,
    MultiImageObjectTypeMeta,
    FacetWithCountType,
)
from .filters import OfficeFilterSet
from .hints import office_resolve_subdivision_set_hint
from .models import Office, Subdivision, Social


class SubdivisionType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип подразделения
    """

    class Meta:
        model = Subdivision
        interfaces = (Node,)
        exclude = ("active",)


class OfficeType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип офиса
    """

    subdivision_set = DjangoListField(SubdivisionType)

    class Meta:
        model = Office
        interfaces = (Node,)
        connection_class = ExtendedConnection
        exclude = ("active", "comment")
        filterset_class = OfficeFilterSet

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset.filter_active()

    @staticmethod
    @resolver_hints(prefetch_related=office_resolve_subdivision_set_hint)
    def resolve_subdivision_set(obj, info, **kwargs):
        return getattr(obj, "subdivision_set")


class SocialType(OptimizedDjangoObjectType):
    """
    Тип социальной сети
    """

    class Meta:
        model = Social
        interfaces = (Node,)


class OfficeQuery(ObjectType):
    """
    Запросы офисов
    """

    all_socials = List(SocialType, description="Социальные сети")
    all_offices = DjangoFilterConnectionField(OfficeType, description="Фильтр по офисам")

    all_offices_facets = FacetFilterField(
        FacetWithCountType,
        filtered_type=OfficeType,
        filterset_class=OfficeFilterSet,
        method_name="facets",
        description="Фасеты для фильтра по квартирам",
    )
    all_offices_specs = FacetFilterField(
        List(SpecType),
        filtered_type=OfficeType,
        filterset_class=OfficeFilterSet,
        method_name="specs",
        description="Спеки для фильтра по квартирам",
    )

    @staticmethod
    def resolve_all_offices(obj, info, **kwargs):
        return query(OfficeType.get_queryset(Office.objects.all(), info), info)

    @staticmethod
    def resolve_all_socials(obj, info, **kwargs):
        return query(Social.objects.all(), info)
