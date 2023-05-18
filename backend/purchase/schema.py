from graphene import Node, List, String, Field, ObjectType
from graphene_django_optimizer import OptimizedDjangoObjectType, query
from django.db.models import Q
from graphene_django import DjangoListField
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id
from common.schema import FacetFilterField, FacetWithCountType, SpecType
from .filters import PurchaseFilterSet, PurchaseTypeCategoryFilterSet
from .models import (
    PurchaseType,
    PurchaseTypeStep,
    PurchaseTypeCategory,
    PurchaseAmount,
    PurchaseAmountDescriptionBlock,
    PurchaseFAQ,
)


class PurchaseAmountDescriptionBlockGraphene(OptimizedDjangoObjectType):
    """
    Размер оплаты, блок описания
    """

    class Meta:
        model = PurchaseAmountDescriptionBlock
        interfaces = (Node,)


class PurchaseAmountGraphene(OptimizedDjangoObjectType):
    """
    Размер оплаты
    """

    purchaseamountdescriptionblock_set = DjangoListField(PurchaseAmountDescriptionBlockGraphene)

    class Meta:
        model = PurchaseAmount
        interfaces = (Node,)


class PurchaseTypeStepGraphene(OptimizedDjangoObjectType):
    """
    Тип шага способа покупки
    """

    class Meta:
        model = PurchaseTypeStep
        interfaces = (Node,)


class PurchaseFAQGraphene(OptimizedDjangoObjectType):
    """
    FAQ
    """

    class Meta:
        model = PurchaseFAQ
        interfaces = (Node,)


class PurchaseTypeGraphene(OptimizedDjangoObjectType):
    """
    Тип способа покупки
    """

    purchasetypestep_set = DjangoListField(PurchaseTypeStepGraphene)
    another_purchase_type = List(lambda: PurchaseTypeGraphene)
    purchaseamount_set = DjangoListField(PurchaseAmountGraphene)
    faq = DjangoListField(PurchaseFAQGraphene)

    class Meta:
        model = PurchaseType
        interfaces = (Node,)
        filterset_class = PurchaseFilterSet

    @staticmethod
    def resolve_another_purchase_type(obj, info, **kwargs):
        return PurchaseType.objects.filter(city=obj.city).exclude(pk=obj.pk)


class PurchaseTypeCategoryGraphene(OptimizedDjangoObjectType):
    """
    Тип категории способа покупки
    """

    purchasetype_set = DjangoListField(PurchaseTypeGraphene)

    class Meta:
        model = PurchaseTypeCategory
        interfaces = (Node,)
        filterset_class = PurchaseTypeCategoryFilterSet


class PurchaseTypeQuery(ObjectType):
    """
    Запросы способов покупки
    """

    all_purchase_types = DjangoFilterConnectionField(
        PurchaseTypeGraphene,
        description="Получения списка способов покупки",
    )
    all_purchase_type_categories = DjangoFilterConnectionField(
        PurchaseTypeCategoryGraphene, description="Список категорий способов покупки"
    )

    all_purchase_types_facets = FacetFilterField(
        FacetWithCountType,
        filtered_type=PurchaseTypeGraphene,
        filterset_class=PurchaseFilterSet,
        method_name="facets",
        description="Фасеты для фильтра по способам покупки",
    )
    all_purchase_types_specs = FacetFilterField(
        List(SpecType),
        filtered_type=PurchaseTypeGraphene,
        filterset_class=PurchaseFilterSet,
        method_name="specs",
        description="Спеки для фильтра по способам покупки",
    )

    purchase_type = Field(
        PurchaseTypeGraphene,
        description="Получение способа покупки по id",
        id=String(),
        slug=String(),
    )

    @staticmethod
    def resolve_all_purchase_types(obj, info, **kwargs):
        return query(PurchaseType.objects.filter(), info)

    @staticmethod
    def resolve_purchase_type(obj, info, **kwargs):
        q = Q()
        global_id = kwargs.get("id", None)
        if global_id:
            ids = from_global_id(global_id)[1]
            q &= Q(id=ids)
        return PurchaseType.objects.filter(q).first()

    @staticmethod
    def resolve_all_purchase_type_categories(obj, info, **kwargs):
        return query(PurchaseTypeCategory.objects.all(), info)
