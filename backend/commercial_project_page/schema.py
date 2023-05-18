from graphene import ObjectType, Field, String, List, Int, Float
from graphene_django_optimizer import OptimizedDjangoObjectType, query, resolver_hints

from projects.models import Project
from projects.schema import ProjectType
from common.schema import MultiImageObjectTypeMeta
from .models import *


class MallTeamType(OptimizedDjangoObjectType):
    class Meta:
        model = MallTeam


class MallTeamAdvantageType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    class Meta:
        model = MallTeamAdvantage


class CommercialProjectPageType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """ Тип страницы коммерческого проекта """

    project = Field(ProjectType)

    min_rate = Float()
    min_initial_fee = Int()
    min_commercial_property_price = Int()
    mall_team = Field(MallTeamType)

    class Meta:
        model = CommercialProjectPage

    @classmethod
    def get_queryset(cls, queryset, info):
        return (
            queryset.annotate_min_commercial_property_price()
            .annotate_min_initial_fee()
            .annotate_min_rate()
        )

    @staticmethod
    @resolver_hints(select_related="project")
    def resolve_project(obj, info, **kwargs):
        return Project.objects.annotate_commercial_count().filter(id=obj.project.id).first()

    @staticmethod
    def resolve_mall_team(obj, info, **kwargs):
        return MallTeam.get_solo()

class CommercialInvestCardType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """ Тип карточки инвестиции в коммерческий проект """

    class Meta:
        model = CommercialInvestCard
        exclude = ("commercial_project_page",)


class CommercialProjectGallerySlideType(
    OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta
):
    """ Тип слайда галереи коммерческого проекта """

    class Meta:
        model = CommercialProjectGallerySlide
        exclude = ("commercial_project_page",)


class CommercialProjectPageFormType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """ Тип формы на странице коммерческого проекта """

    class Meta:
        model = CommercialProjectPageForm


class ProjectAudienceType(OptimizedDjangoObjectType):
    """ Тип аудитории проекта """

    class Meta:
        model = ProjectAudience
        exclude = ("commercial_project_page",)


class AudienceAgeType(OptimizedDjangoObjectType):
    """ Тип возраста аудитории """

    class Meta:
        model = AudienceAge
        exclude = ("audience",)


class AudienceFactType(OptimizedDjangoObjectType):
    """ Тип факта аудитории """

    class Meta:
        model = AudienceFact
        exclude = ("audience",)


class AudienceIncomeType(OptimizedDjangoObjectType):
    """ Тип дохода аудитории """

    class Meta:
        model = AudienceIncome
        exclude = ("audience",)


class CommercialProjectComparisonType(OptimizedDjangoObjectType):
    """ Тип сравнения коммерческого проекта """

    class Meta:
        model = CommercialProjectComparison
        exclude = ("commercial_project_page",)


class CommercialProjectComparisonItemType(OptimizedDjangoObjectType):
    """ Тип элемента сравнения коммерческого проекта """

    class Meta:
        model = CommercialProjectComparisonItem
        exclude = ("comparison",)


class CommercialProjectPageQuery(ObjectType):
    """
    Запросы страницы коммерческого проекта
    """

    commercial_project_page = Field(
        CommercialProjectPageType,
        slug=String(required=True),
        description="Получение страницы коммерческого проекта",
    )
    all_commercial_project_comparison = List(
        CommercialProjectComparisonType,
        slug=String(required=True),
        description="Получение всех сравнений коммерческого проекта",
    )

    @staticmethod
    def resolve_commercial_project_page(obj, info, **kwargs):
        slug = kwargs.get("slug")
        return query(
            CommercialProjectPageType.get_queryset(
                CommercialProjectPage.objects.filter(slug=slug), info
            ),
            info,
        ).first()

    @staticmethod
    def resolve_all_commercial_project_comparison(obj, info, **kwargs):
        slug = kwargs.get("slug")
        return query(
            CommercialProjectComparison.objects.filter(commercial_project_page__slug=slug), info
        )
