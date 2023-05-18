from graphene import ObjectType, Node
from graphene_django_optimizer import OptimizedDjangoObjectType, query
from graphene_django import DjangoConnectionField

from .models import (
    DevLandAbout,
    DevLandBanner,
    DevLandSecondBanner,
    DevLandThirdBanner,
    DevLandCheckBoxesTitle,
    DevLandCheckBoxes,
    DevLandMap
)


class AboutType(OptimizedDjangoObjectType):
    """
    Тип главного раздела
    """
    class Meta:
        model = DevLandAbout
        interfaces = (Node,)


class BannerType(OptimizedDjangoObjectType):
    """
    Тип основных баннеров на главной странице
    """
    class Meta:
        model = DevLandBanner
        interfaces = (Node,)


class SecondBannerType(OptimizedDjangoObjectType):
    """
    Тип верхних баннеров
    """
    class Meta:
        model = DevLandSecondBanner
        interfaces = (Node,)


class ThirdBannerType(OptimizedDjangoObjectType):
    """
    Тип нижних баннеров
    """
    class Meta:
        model = DevLandThirdBanner
        interfaces = (Node,)


class CheckBoxesTitleType(OptimizedDjangoObjectType):
    """
    Тип описания раздела чекбоксов
    """
    class Meta:
        model = DevLandCheckBoxesTitle
        interfaces = (Node,)


class CheckBoxesType(OptimizedDjangoObjectType):
    """
    Тип чекбоксов
    """
    class Meta:
        model = DevLandCheckBoxes
        interfaces = (Node,)


class MapValuesType(OptimizedDjangoObjectType):
    """
    Тип данных на карте
    """
    class Meta:
        model = DevLandMap
        interfaces = (Node,)


class DevelopersLandownersQuery(ObjectType):
    all_about = DjangoConnectionField(AboutType, description='главный баннер')
    all_banner = DjangoConnectionField(BannerType, description='подбаннеры')
    all_second_banner = DjangoConnectionField(
        SecondBannerType,
        description='главный баннер на второй странице'
    )
    all_third_banner = DjangoConnectionField(
        ThirdBannerType,
        description='подбаннер внизу второй'
    )
    all_checkbox_title = DjangoConnectionField(
        CheckBoxesTitleType,
        description='Описание чекбоксов'
    )
    all_checkboxes = DjangoConnectionField(CheckBoxesType, description='Чекбоксы')
    all_map_values = DjangoConnectionField(MapValuesType, description='Значения на карте')

    @staticmethod
    def resolve_all_about(obj, info, **kwargs):
        return query(DevLandAbout.objects.all(), info)

    @staticmethod
    def resolve_all_banner(obj, info, **kwargs):
        return query(DevLandBanner.objects.all(), info)

    @staticmethod
    def resolve_all_second_banner(obj, info, **kwargs):
        return query(DevLandSecondBanner.objects.all(), info)

    @staticmethod
    def resolve_all_third_banner(obj, info, **kwargs):
        return query(DevLandThirdBanner.objects.all(), info)

    @staticmethod
    def resolve_all_checkbox_title(obj, info, **kwargs):
        return query(DevLandCheckBoxesTitle.objects.all(), info)

    @staticmethod
    def resolve_all_checkboxes(obj, info, **kwargs):
        return query(DevLandCheckBoxes.objects.all(), info)

    @staticmethod
    def resolve_all_map_values(obj, info, **kwargs):
        return query(DevLandMap.objects.all(), info)
