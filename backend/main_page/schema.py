from graphene import ObjectType, Field, List
from graphene_django_optimizer import OptimizedDjangoObjectType, resolver_hints, query
from common.schema import MultiImageObjectTypeMeta
from .hints import (
    main_page_resolve_slides_hint,
    main_page_resolve_stories_hint,
    main_page_story_resolve_images_hint,
)
from .models import (
    MainPage,
    MainPageSlide,
    MainPageIdeologyCard,
    MapText,
    MainPageStory,
    MainPageStoryImage,
)


class MainPageType(OptimizedDjangoObjectType):
    """
    Тип главной страницы
    """

    slides = List("main_page.schema.MainPageSlideType")
    stories = List("main_page.schema.MainPageStoryType")

    class Meta:
        model = MainPage

    @staticmethod
    @resolver_hints(prefetch_related=main_page_resolve_slides_hint)
    def resolve_slides(obj, info, **kwargs):
        return getattr(obj, "prefetched_slides")

    @staticmethod
    @resolver_hints(prefetch_related=main_page_resolve_stories_hint)
    def resolve_stories(obj, info, **kwargs):
        return getattr(obj, "prefetched_stories")


class MapTextType(OptimizedDjangoObjectType):
    """
    Тип текста на карте
    """

    class Meta:
        model = MapText


class MainPageStoryType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """ Тип истории с главной страницы """

    images = List("main_page.schema.MainPageStoryImageType")

    class Meta:
        model = MainPageStory

    @staticmethod
    @resolver_hints(prefetch_related=main_page_story_resolve_images_hint)
    def resolve_images(obj, info, **kwargs):
        return getattr(obj, "prefetched_images")


class MainPageStoryImageType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """ Тип изображения истории с главной страницы """

    class Meta:
        model = MainPageStoryImage


class MainPageSlideType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип слайда на главной странице
    """

    class Meta:
        model = MainPageSlide


class MainPageIdeologyCartType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип карточки идеологии на главной странице
    """

    class Meta:
        model = MainPageIdeologyCard


class MainPageQuery(ObjectType):
    """
    Запросы главной страницы
    """

    main_page = Field(MainPageType, description="Главная страница")

    @staticmethod
    def resolve_main_page(obj, info, **kwargs):
        current_site = info.context.site
        return query(MainPage.objects.filter(site=current_site.id), info).first()
