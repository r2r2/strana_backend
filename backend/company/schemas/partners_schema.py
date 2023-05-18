from graphene import ObjectType, Field
from graphene_django_optimizer import OptimizedDjangoObjectType
from ..models import PartnersPage, PartnersPageBlock


class PartnersPageBlockType(OptimizedDjangoObjectType):
    """
    Тип блока страницы партнеров
    """

    class Meta:
        model = PartnersPageBlock
        exclude = ("page",)


class PartnersPageType(OptimizedDjangoObjectType):
    """
    Тип страницы партнеров
    """

    class Meta:
        model = PartnersPage


class PartnersQuery(ObjectType):
    """
    Запросы партнеров
    """

    partners_page = Field(PartnersPageType, description="Страница партнеров")

    @staticmethod
    def resolve_partners_page(obj, info, **kwargs):
        return PartnersPage.get_solo()
