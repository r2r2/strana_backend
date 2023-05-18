from graphene import ObjectType, Field, List, Node, String
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django_optimizer import OptimizedDjangoObjectType, query, resolver_hints
from common.schema import MultiImageObjectTypeMeta
from common.graphene import ExtendedConnection
from ..filters import OffersDocumentFilter
from ..hints import story_resolve_images_hint
from ..models import (
    AboutPage,
    IdeologySlider,
    IdeologyCard,
    Achievement,
    OffersDocument,
    LargeTenant,
    Person,
    Story,
    StoryImage,
    CompanyValue,
)


class AchievementType(OptimizedDjangoObjectType):
    """
    Тип достижения
    """

    class Meta:
        model = Achievement
        exclude = ("about_section",)


class IdeologyCardType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип карточки идеологии
    """

    class Meta:
        model = IdeologyCard
        exclude = ("about_section",)


class CompanyValueType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип ценности компании
    """

    class Meta:
        model = CompanyValue
        exclude = ("about_section",)


class IdeologySliderType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип слайдера идеологии
    """

    class Meta:
        model = IdeologySlider
        exclude = ("about_section",)


class StoryImageType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип изображения истории о компании
    """

    class Meta:
        model = StoryImage


class StoryType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип истории о компании
    """

    images = List(StoryImageType)

    class Meta:
        model = Story
        exclude = ("about_section",)

    @staticmethod
    @resolver_hints(prefetch_related=story_resolve_images_hint)
    def resolve_images(obj, info, **kwargs):
        return getattr(obj, "prefetched_images")


class LargeTenantType(OptimizedDjangoObjectType):
    """
    Тип крупного арендатора
    """

    class Meta:
        model = LargeTenant
        exclude = ("about_section",)


class AboutPageType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип страницы о компании
    """

    class Meta:
        model = AboutPage


class PersonType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип персоны
    """

    class Meta:
        model = Person


class OffersDocumentType(OptimizedDjangoObjectType):
    """
    Тип документов оферты и политика обработки данных
    """

    class Meta:
        model = OffersDocument
        interfaces = (Node,)
        convert_choices_to_enum = False
        connection_class = ExtendedConnection
        filterset_class = OffersDocumentFilter


class AboutQuery(ObjectType):
    """
    Запросы страницы о компании
    """

    about_page = Field(AboutPageType, description="Страница о компании")
    all_offers_document = DjangoFilterConnectionField(
        OffersDocumentType, description="Фильтр по вакансиям"
    )
    all_persons = List(
        PersonType, category=String(required=True), description="Получение всех персон по категории"
    )

    @staticmethod
    def resolve_about_page(obj, info, **kwargs):
        return query(AboutPage.objects.all(), info).first()

    @staticmethod
    def resolve_all_persons(obj, info, category, **kwargs):
        return query(Person.objects.filter(category=category), info)
