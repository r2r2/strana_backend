from graphene import Field, Node, ObjectType, List, ID
from graphene_django_optimizer import OptimizedDjangoObjectType, query
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id
from common.graphene import ExtendedConnection
from common.schema import FacetFilterField, SpecType, FacetWithCountType, MultiImageObjectTypeMeta
from ..filters import VacancyFilterSet
from ..models import (
    Vacancy,
    VacancyCategory,
    VacancyPage,
    VacancyPageAdvantage,
    VacancyPageForm,
    VacancyPageFormEmployee,
)


class VacancyPageAdvantageType(OptimizedDjangoObjectType):
    """
    Тип преимущества страницы вакансий
    """

    class Meta:
        model = VacancyPageAdvantage


class VacancyPageFormType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип формы странины вакансий
    """

    class Meta:
        model = VacancyPageForm


class VacancyPageFormEmployeeType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип сотрудника формы странины вакансий
    """

    class Meta:
        model = VacancyPageFormEmployee


class VacancyPageType(OptimizedDjangoObjectType):
    """
    Тип страницы вакансий
    """

    class Meta:
        model = VacancyPage


class VacancyType(OptimizedDjangoObjectType):
    """
    Тип вакансии
    """

    class Meta:
        model = Vacancy
        interfaces = (Node,)
        convert_choices_to_enum = False
        connection_class = ExtendedConnection
        filterset_class = VacancyFilterSet

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset.filter(city__active=True)


class VacancyCategoryType(DjangoObjectType):
    """
    Тип категории вакансий
    """

    class Meta:
        model = VacancyCategory
        interfaces = (Node,)
        exclude = ("vacancy_set",)


class VacancyQuery(ObjectType):
    """
    Запросы вакансий
    """

    all_vacancies = DjangoFilterConnectionField(VacancyType, description="Фильтр по вакансиям")

    all_vacancies_facets = FacetFilterField(
        FacetWithCountType,
        filtered_type=VacancyType,
        filterset_class=VacancyFilterSet,
        method_name="facets",
        description="Фасеты для фильтра по вакансиям",
    )
    all_vacancies_specs = FacetFilterField(
        List(SpecType),
        filtered_type=VacancyType,
        filterset_class=VacancyFilterSet,
        method_name="specs",
        description="Спеки для фильтра по вакансиям",
    )

    vacancy_page = Field(VacancyPageType, description="Страница вакансий")
    vacancy_forms_employee = List(
        VacancyPageFormEmployeeType, 
        city=ID(),
        description="Cотрудники формы странины вакансий",
    )

    @staticmethod
    def resolve_vacancy_page(obj, info, **kwargs):
        return VacancyPage.get_solo()

    @staticmethod
    def resolve_all_vacancies(obj, info, **kwargs):
        return query(Vacancy.objects.filter(is_active=True).distinct(), info)

    @staticmethod
    def resolve_vacancy_forms_employee(obj, info, **kwargs):
        qs = VacancyPageFormEmployee.objects.all() 
        if kwargs.get("city"): 
            try: 
                _, city_id = from_global_id(kwargs.get("city")) 
                return query(qs.filter(city=city_id), info) 
            except (UnicodeDecodeError, BinasciiError, ValueError): 
                return None 
        return query(qs, info)
