from graphene_django_optimizer import OptimizedDjangoObjectType, query
from graphene import ObjectType, Node
from graphene_django.filter import DjangoFilterConnectionField

from .models import PopUpInfo, PopUpTag
from .filters import PopUpInfoFilter, PopUpTagFilter


class PopUpTagType(OptimizedDjangoObjectType):
    """
    Тип поп-апа
    """

    class Meta:
        model = PopUpTag
        interfaces = (Node,)
        filterset_class = PopUpTagFilter


class PopUpInfoType(OptimizedDjangoObjectType):
    """
    Данные поп-апа
    """

    class Meta:
        model = PopUpInfo
        interfaces = (Node,)
        filterset_class = PopUpInfoFilter


class PopUpQuery(ObjectType):
    """
    Запросы поп-ап
    """
    pop_up_info = DjangoFilterConnectionField(PopUpInfoType, description="Поп-ап")
    pop_up_tag = DjangoFilterConnectionField(PopUpTagType, description="Тип Поп-апа")

    @staticmethod
    def resolve_pop_up_info(obj, info, **kwargs):
        return query(PopUpInfo.objects.all(), info)

    @staticmethod
    def resolve_pop_up_tag(obj, info, **kwargs):
        return query(PopUpTag.objects.all(), info)
