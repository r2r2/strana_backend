from graphene_django_optimizer import OptimizedDjangoObjectType, query
from graphene import ObjectType, Node
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django import DjangoConnectionField

from .models import (
    YieldComparison,
    InvestmentTypes,
    RentalBusinessSales,
    MainBanner,
    Banner,
    SecondBanner,
    LastBanner,
    OwnEyeLooking,
)
from .filters import YieldComparisonFilter, InvestmentTypesFilter, RentalBusinessSalesFilter


class YieldComparisonType(OptimizedDjangoObjectType):
    """
    Тип сравнения доходности
    """

    class Meta:
        model = YieldComparison
        interfaces = (Node,)
        filterset_class = YieldComparisonFilter


class InvestmentTypesType(OptimizedDjangoObjectType):
    """
    Тип видов инвестиций
    """

    class Meta:
        model = InvestmentTypes
        interfaces = (Node,)
        filterset_class = InvestmentTypesFilter
        convert_choices_to_enum = False


class RentalBusinessSalesType(OptimizedDjangoObjectType):
    """
    Тип кейсов продаж арендного бизнеса
    """

    class Meta:
        model = RentalBusinessSales
        interfaces = (Node,)
        filterset_class = RentalBusinessSalesFilter


class MainBannerType(OptimizedDjangoObjectType):
    """
    Тип баннера about
    """

    class Meta:
        model = MainBanner
        interfaces = (Node,)


class InvestmentBannerType(OptimizedDjangoObjectType):
    """
    Тип баннера №1
    """

    class Meta:
        model = Banner
        interfaces = (Node,)


class InvestmentSecondBannerType(OptimizedDjangoObjectType):
    """
    Тип баннера №2
    """

    class Meta:
        model = SecondBanner
        interfaces = (Node,)


class InvestmentLastBannerType(OptimizedDjangoObjectType):
    """
    Тип баннера №3
    """

    class Meta:
        model = LastBanner
        interfaces = (Node,)


class InvestmentOwnEyeLookingType(OptimizedDjangoObjectType):
    """
    Тип посмотрите своими глазами
    """

    class Meta:
        model = OwnEyeLooking
        interfaces = (Node,)


class InvestmentsQuery(ObjectType):
    """
    Запросы инвестиций
    """

    yield_comparison = DjangoFilterConnectionField(YieldComparisonType, description="сравнение доходности")
    investment_types = DjangoFilterConnectionField(InvestmentTypesType, description="виды инвестиций")
    rental_business_sales = DjangoFilterConnectionField(
        RentalBusinessSalesType,
        description="кейсы продаж арендного бизнеса"
    )
    main_banner = DjangoConnectionField(MainBannerType, description='тип баннера about')
    banner = DjangoConnectionField(InvestmentBannerType, description='тип баннера 1')
    second_banner = DjangoConnectionField(InvestmentSecondBannerType, description='тип баннера 2')
    last_banner = DjangoConnectionField(InvestmentLastBannerType, description='тип баннера 3')
    own_eye_looking = DjangoConnectionField(InvestmentOwnEyeLookingType, description='баннер посмотрите своими глазами')

    @staticmethod
    def resolve_yield_comparison(obj, info, **kwargs):
        return query(YieldComparison.objects.all().order_by('order'), info)

    @staticmethod
    def resolve_investment_types(obj, info, **kwargs):
        return query(InvestmentTypes.objects.all().order_by('order'), info)

    @staticmethod
    def resolve_rental_business_sales(obj, info, **kwargs):
        return query(RentalBusinessSales.objects.all().order_by('order'), info)

    @staticmethod
    def resolve_main_banner(obj, info, **kwargs):
        return query(MainBanner.objects.all(), info)

    @staticmethod
    def resolve_banner(obj, info, **kwargs):
        return query(Banner.objects.all(), info)

    @staticmethod
    def resolve_second_banner(obj, info, **kwargs):
        return query(SecondBanner.objects.all(), info)

    @staticmethod
    def resolve_last_banner(obj, info, **kwargs):
        return query(LastBanner.objects.all(), info)

    @staticmethod
    def resolve_own_eye_looking(obj, info, **kwargs):
        return query(OwnEyeLooking.objects.all(), info)
