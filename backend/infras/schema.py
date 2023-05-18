from graphene import Node, ObjectType
from graphene_django_optimizer import OptimizedDjangoObjectType, query
from graphene_django.filter import DjangoFilterConnectionField
from common.graphene_connection import ExtendedConnection
from .filters import (
    InfraCategoryFilter,
    InfraFilter,
    MainInfraFilter,
    SubInfraFilter,
    RoundInfraFilter,
)
from .models import (
    Infra,
    InfraCategory,
    InfraType,
    InfraContent,
    MainInfraContent,
    MainInfra,
    SubInfra,
    RoundInfra,
)


class InfraGraphene(OptimizedDjangoObjectType):
    """
    Тип инфраструктуры на карте
    """

    class Meta:
        model = Infra
        interfaces = (Node,)
        filterset_class = InfraFilter
        convert_choices_to_enum = False
        connection_class = ExtendedConnection


class MainInfraGraphene(OptimizedDjangoObjectType):
    """
    Тип главной инфраструктуры на генплане
    """

    class Meta:
        model = MainInfra
        interfaces = (Node,)
        filterset_class = MainInfraFilter
        connection_class = ExtendedConnection


class SubInfraGraphene(OptimizedDjangoObjectType):
    """
    Тип дополнительной инфраструктуры на генплане
    """

    class Meta:
        model = SubInfra
        interfaces = (Node,)
        filterset_class = SubInfraFilter
        connection_class = ExtendedConnection


class RoundInfraGraphene(OptimizedDjangoObjectType):
    """
    Тип окружной инфраструктуры на генплане
    """

    class Meta:
        model = RoundInfra
        interfaces = (Node,)
        filterset_class = RoundInfraFilter
        connection_class = ExtendedConnection


class InfraCategoryGraphene(OptimizedDjangoObjectType):
    """
    Тип категорий инфраструктур на карте
    """

    class Meta:
        model = InfraCategory
        interfaces = (Node,)
        filterset_class = InfraCategoryFilter
        connection_class = ExtendedConnection


class InfraTypeGraphene(OptimizedDjangoObjectType):
    """
    Тип типа инфраструктур на карте
    """

    class Meta:
        model = InfraType


class InfraContentGraphene(OptimizedDjangoObjectType):
    """
    Тип контента инфраструктур на карте
    """

    class Meta:
        model = InfraContent


class MainInfraContentGraphene(OptimizedDjangoObjectType):
    """
    Тип контента главных инфраструктур на генплане
    """

    class Meta:
        model = MainInfraContent


class InfraQuery(ObjectType):
    """
    Запросы инфраструктур
    """

    all_infra = DjangoFilterConnectionField(InfraGraphene, description="Список инфраструктур")
    all_infra_categories = DjangoFilterConnectionField(
        InfraCategoryGraphene, description="Список категорий инфраструктур"
    )

    all_main_infra = DjangoFilterConnectionField(
        MainInfraGraphene, description="Список главных инфраструктур"
    )
    all_sub_infra = DjangoFilterConnectionField(
        SubInfraGraphene, description="Список дополнительных инфраструктур"
    )
    all_round_infra = DjangoFilterConnectionField(
        RoundInfraGraphene, description="Список окружных инфраструктур"
    )

    @staticmethod
    def resolve_all_infra_categories(obj, info, **kwargs):
        return query(InfraCategory.objects.distinct(), info)

    @staticmethod
    def resolve_all_infra(obj, info, **kwargs):
        return query(Infra.objects.all(), info)

    @staticmethod
    def resolve_all_main_infra(obj, info, **kwargs):
        return query(MainInfra.objects.all(), info)

    @staticmethod
    def resolve_all_sub_infra(obj, info, **kwargs):
        return query(SubInfra.objects.all(), info)

    @staticmethod
    def resolve_all_round_infra(obj, info, **kwargs):
        return query(RoundInfra.objects.all(), info)
