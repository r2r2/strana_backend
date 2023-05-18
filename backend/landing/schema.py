from binascii import Error as BinasciiError
from graphql_relay import to_global_id, from_global_id
from graphene import ObjectType, List, Field, String, ID
from graphene_django_optimizer import OptimizedDjangoObjectType, query, resolver_hints

from news.schema import NewsType
from common.schema import MultiImageObjectTypeMeta
from properties.schema import FurnishType, GlobalFlatType
from .hints import (
    block_resolve_furnishes_hint,
    block_resolve_progress_set_hint,
    block_resolve_news_set_hint,
    block_resolve_flat_set_hint,
)
from .models import *


class LandingType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """Тип лендинга"""

    bars = List(List(String))
    block_ids = List(ID)

    class Meta:
        model = Landing
        exclude = ("landing_news",)

    @staticmethod
    def resolve_bars(obj, info, **kwargs):
        return list(obj.landingblock_set.exclude(title="").values_list("title", "anchor"))

    @staticmethod
    def resolve_block_ids(obj, info, **kwargs):
        ids = [
            to_global_id(LandingBlockType.__name__, block.id)
            for block in obj.landingblock_set.all()
        ]
        return ids


class LandingBlockType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """Тип блока с текстом и тремя изображениями"""

    furnishes = List(FurnishType)
    news_set = List(NewsType)
    progress_set = List(NewsType)
    flat_set = List(GlobalFlatType)

    class Meta:
        model = LandingBlock
        exclude = ("landing",)
        convert_choices_to_enum = False

    @staticmethod
    @resolver_hints(prefetch_related=block_resolve_furnishes_hint)
    def resolve_furnishes(obj, info, **kwargs):
        return getattr(obj, "prefetched_furnishes")

    @staticmethod
    @resolver_hints(prefetch_related=block_resolve_progress_set_hint)
    def resolve_progress_set(obj, info, **kwargs):
        return getattr(obj, "prefetched_progress_set")

    @staticmethod
    @resolver_hints(prefetch_related=block_resolve_news_set_hint)
    def resolve_news_set(obj, info, **kwargs):
        return getattr(obj, "prefetched_news_set")

    @staticmethod
    @resolver_hints(prefetch_related=block_resolve_flat_set_hint)
    def resolve_flat_set(obj, info, **kwargs):
        return getattr(obj, "prefetched_flat_set")


class TwoColumnsBlockItemType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """Тип элемента блока c иконками в две колонки"""

    class Meta:
        model = TwoColumnsBlockItem
        exclude = ("block",)


class SliderBlockSlideType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """Тип слайда блока слайдера"""

    class Meta:
        model = SliderBlockSlide
        exclude = ("block",)


class AdvantageBlockItemType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """Тип элемента блока преимуществ"""

    class Meta:
        model = AdvantageBlockItem
        exclude = ("block",)


class DigitsBlockItemType(OptimizedDjangoObjectType):
    """Тип элемента блока цифры"""

    class Meta:
        model = DigitsBlockItem
        exclude = ("block",)


class StepsBlockItemType(OptimizedDjangoObjectType):
    """Тип элемента блока шаги"""

    class Meta:
        model = StepsBlockItem
        exclude = ("block",)


class ListBlockItemType(OptimizedDjangoObjectType):
    """Тип элемента блока со списоком"""

    class Meta:
        model = ListBlockItem
        exclude = ("block",)


class LandingQuery(ObjectType):
    all_landings = List(LandingType, description="Получение всех лендингов")
    landing = Field(
        LandingType, slug=String(required=True), description="Получение лендинга по slug"
    )
    landing_block = Field(
        LandingBlockType, id=ID(required=True), description="Получение блока лендинга по id"
    )

    @staticmethod
    def resolve_all_landings(obj, info, **kwargs):
        return query(Landing.objects.filter_active(), info)

    @staticmethod
    def resolve_landing(obj, info, **kwargs):
        slug = kwargs.get("slug")
        return query(Landing.objects.filter_active().filter(slug=slug), info).first()

    @staticmethod
    def resolve_landing_block(obj, info, **kwargs):
        _id = kwargs.get("id")
        if _id:
            try:
                _, _id = from_global_id(_id)
                return query(LandingBlock.objects.filter(id=_id), info).first()
            except (UnicodeDecodeError, BinasciiError, ValueError):
                pass
