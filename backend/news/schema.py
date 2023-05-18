from html import unescape
from django.template.defaultfilters import truncatechars_html
from graphene_django_optimizer import query
from graphene import Node, String, AbstractType, List, Int, ObjectType, Field
from graphene_django_optimizer import OptimizedDjangoObjectType, resolver_hints
from graphene_django import DjangoListField
from graphene_django.filter import DjangoFilterConnectionField
from common.schema import FacetFilterField, SpecType, FacetWithCountType, MultiImageObjectTypeMeta
from common.scalars import File
from common.graphene import ExtendedConnection
from projects.schema import ProjectType
from .constants import NewsType as ModelNewsType
from .filters import NewsFilterSet, ProgressFilterSet
from .models import News, NewsSlide, MassMedia, NewsForm
from .hints import (
    progress_resolve_slide_set_hint,
    news_resolve_image_slide_set_hint,
    news_resolve_video_slide_set_hint,
)


class BaseNewsType(AbstractType):
    """
    Базовый тип новостей
    """

    color = String()
    projects = DjangoListField(ProjectType)

    @staticmethod
    def resolve_color(obj, info, **kwargs):
        res = obj.projects.first()
        if res:
            return res.color
        return None

    @staticmethod
    def resolve_projects(obj, info, **kwargs):
        return obj.projects


class MassMediaType(OptimizedDjangoObjectType):
    """ Тип СМИ """

    logo = File()

    class Meta:
        model = MassMedia


class NewsFormType(OptimizedDjangoObjectType):
    """ Тип формы на странице новости """

    class Meta:
        model = NewsForm


class NewsSlideType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип слайда новости
    """

    class Meta:
        model = NewsSlide
        interfaces = (Node,)
        connection_class = ExtendedConnection
        exclude = ("image", "preview")


class ProgressType(OptimizedDjangoObjectType, BaseNewsType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип хода строительства
    """

    slide_set = List(NewsSlideType, first=Int())

    slide_set_count = Int()
    quarter = String()

    class Meta:
        model = News
        interfaces = (Node,)
        connection_class = ExtendedConnection
        exclude = ("card_image", "image")
        convert_choices_to_enum = False
        filterset_class = ProgressFilterSet

    @classmethod
    def get_queryset(cls, queryset, info):
        return (
            queryset.filter(type=ModelNewsType.PROGRESS, date__isnull=False, published=True)
            .filter_timeframed()
            .annotate_quarter()
        )

    @staticmethod
    @resolver_hints(prefetch_related=progress_resolve_slide_set_hint)
    def resolve_slide_set(obj, info, **kwargs):
        slide_set = getattr(obj, "slide_set")
        first = kwargs.get("first", None)
        if first:
            slide_set = slide_set[:first]
        return slide_set

    @staticmethod
    def resolve_slide_set_count(obj, info, **kwargs):
        slide_set = getattr(obj, "slide_set")
        slide_set_count = 0
        if slide_set:
            slide_set_count = len(slide_set)
        return slide_set_count


class NewsType(OptimizedDjangoObjectType, BaseNewsType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип новости
    """

    short_description = String()
    image_slide_set = List(NewsSlideType)
    video_slide_set = List(NewsSlideType)
    another_news = List(lambda: NewsType, limit=Int(required=True))

    class Meta:
        model = News
        interfaces = (Node,)
        connection_class = ExtendedConnection
        exclude = ("card_image", "image", "newsslide_set")
        convert_choices_to_enum = False
        filterset_class = NewsFilterSet

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset.active()

    @staticmethod
    def resolve_short_description(obj, info, **kwargs):
        text = obj.short_description or obj.text
        if len(text) > 430:
            return truncatechars_html(unescape(text), 430)
        return text

    @staticmethod
    @resolver_hints(prefetch_related=news_resolve_image_slide_set_hint)
    def resolve_image_slide_set(obj, info, **kwargs):
        return obj.imageslide_set

    @staticmethod
    @resolver_hints(prefetch_related=news_resolve_video_slide_set_hint)
    def resolve_video_slide_set(obj, info, **kwargs):
        return obj.videoslide_set

    @staticmethod
    def resolve_another_news(obj, info, limit, **kwargs):
        return query(obj.another_news[:limit], info)


class NewsQuery(ObjectType):
    """
    Запросы новостей
    """

    all_news = DjangoFilterConnectionField(NewsType, description="Фильтр новостей")
    all_progress = DjangoFilterConnectionField(
        ProgressType, description="Фильтр по прогрессу строительства"
    )

    all_news_facets = FacetFilterField(
        FacetWithCountType,
        filtered_type=NewsType,
        filterset_class=NewsFilterSet,
        method_name="facets",
        description="Фасеты для фильтра по новостям",
    )
    all_news_specs = FacetFilterField(
        List(SpecType),
        filtered_type=NewsType,
        filterset_class=NewsFilterSet,
        method_name="specs",
        description="Спеки для фильтра по новостям",
    )
    all_progress_facets = FacetFilterField(
        FacetWithCountType,
        filtered_type=ProgressType,
        filterset_class=ProgressFilterSet,
        method_name="facets",
        description="Фасеты для фильтра прогресса строительства",
    )
    all_progress_specs = FacetFilterField(
        List(SpecType),
        filtered_type=ProgressType,
        filterset_class=ProgressFilterSet,
        method_name="specs",
        description="Спеки для фильтра прогресса строительства",
    )

    news = Field(NewsType, slug=String(required=True), description="Получение новости по slug")
    progress = Field(
        ProgressType, slug=String(required=True), description="Получение прогресса по slug"
    )

    @staticmethod
    def resolve_all_news(obj, info, **kwargs):
        queryset = NewsType.get_queryset(News.objects.annotate_color(), info)
        return query(queryset, info).distinct()

    @staticmethod
    def resolve_news(obj, info, **kwargs):
        slug = kwargs.get("slug")
        try:
            return query(NewsType.get_queryset(News.objects.annotate_color(), info), info).get(
                slug=slug
            )
        except News.DoesNotExist:
            return None

    @staticmethod
    def resolve_all_progress(obj, info, **kwargs):
        return query(
            ProgressType.get_queryset(News.objects.annotate_color(), info), info
        ).distinct()

    @staticmethod
    def resolve_progress(obj, info, **kwargs):
        slug = kwargs.get("slug")
        try:
            return query(ProgressType.get_queryset(News.objects.annotate_color(), info), info).get(
                slug=slug
            )
        except News.DoesNotExist:
            return None
