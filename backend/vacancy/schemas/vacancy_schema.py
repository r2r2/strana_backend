from graphene import Field, Node, ObjectType, List, ID, Int, String
from graphene_django_optimizer import OptimizedDjangoObjectType, query
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from common.graphene import ExtendedConnection
from common.schema import FacetFilterField, SpecType, FacetWithCountType, MultiImageObjectTypeMeta
from graphql_relay import from_global_id
from ..filters import VacancyFilterSet
from ..models import (
    Vacancy,
    VacancyCategory,
    VacancyPageAdvantage,
    VacancyPageForm,
    VacancyPageFormEmployee,
    VacancyAbout,
    VacancyShouldWork,
    VacancyShouldWorkSlider,
    VacancySlider,
    VacancyEmployees,
    VacancyDescription,
)


class VacancyDescriptionType1(OptimizedDjangoObjectType):
    """
    Тип описания вакансий
    """

    class Meta:
        model = VacancyDescription


class VacancyPageAdvantageType1(OptimizedDjangoObjectType):
    """
    Тип преимущества страницы вакансий
    """

    class Meta:
        model = VacancyPageAdvantage


class VacancyPageFormType1(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип формы странины вакансий
    """

    class Meta:
        model = VacancyPageForm


class VacancyPageFormEmployeeType1(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип сотрудника формы странины вакансий
    """

    class Meta:
        model = VacancyPageFormEmployee


class VacancyType1(OptimizedDjangoObjectType):
    """
    Тип вакансии
    """
    description = List(VacancyDescriptionType1)
    work_format = String()

    class Meta:
        model = Vacancy
        interfaces = (Node,)
        convert_choices_to_enum = False
        connection_class = ExtendedConnection
        filterset_class = VacancyFilterSet

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset.filter(city__active=True)

    @staticmethod
    def resolve_description(obj, info, **kwargs):
        return query(VacancyDescription.objects.filter(vacancy=obj), info)

    @staticmethod
    def resolve_work_format(obj, info, **kwargs):
        if obj.work_format:
            return obj.work_format.name
        return ""


class VacancyCategoryType1(DjangoObjectType):
    """
    Тип категории вакансий
    """

    class Meta:
        model = VacancyCategory
        interfaces = (Node,)
        exclude = ("vacancy_set",)

    vacancy_count = Int()

    @staticmethod
    def resolve_vacancy_count(root, info, **kwargs):
        return query(Vacancy.objects.filter(
            category=root.id,
            is_active=True,
            city__isnull=False
        ).distinct().count(), info)


class VacancyAboutType(OptimizedDjangoObjectType):
    """
    Тип о компании
    """

    class Meta:
        model = VacancyAbout
        interfaces = (Node, )


class VacancyShouldWorkType(OptimizedDjangoObjectType):
    """
    Тип почему вам стоит работать
    """

    class Meta:
        model = VacancyShouldWork
        interfaces = (Node, )


class VacancyShouldWorkSliderType(OptimizedDjangoObjectType):
    """
    Тип почему вам стоит работать ( слайдер )
    """

    class Meta:
        model = VacancyShouldWorkSlider
        interfaces = (Node, )


class VacancySliderType(OptimizedDjangoObjectType):
    """
    Тип cлайдер ( кадры нашей жизни )
    """

    class Meta:
        model = VacancySlider
        interfaces = (Node, )


class VacancyEmployeesType(OptimizedDjangoObjectType):
    """
    Сотрудники
    """

    class Meta:
        model = VacancyEmployees
        interfaces = (Node, )


class VacancyDescriptionType(OptimizedDjangoObjectType):
    """
    Описание вакансии
    """

    class Meta:
        model = VacancyDescription
        interfaces = (Node, )


class VacancyQuery(ObjectType):
    """
    Запросы вакансий
    """

    all_vacancies_1 = DjangoFilterConnectionField(VacancyType1, description="Фильтр по вакансиям")
    vacancies_1 = Field(
        VacancyType1, id=ID(required=True), description="Получение вакансии по ID"
    )

    all_vacancies_facets_1 = FacetFilterField(
        FacetWithCountType,
        filtered_type=VacancyType1,
        filterset_class=VacancyFilterSet,
        method_name="facets",
        description="Фасеты для фильтра по вакансиям",
    )
    all_vacancies_specs_1 = FacetFilterField(
        List(SpecType),
        filtered_type=VacancyType1,
        filterset_class=VacancyFilterSet,
        method_name="specs",
        description="Спеки для фильтра по вакансиям",
    )

    vacancy_forms_employee_1 = List(
        VacancyPageFormEmployeeType1,
        city=ID(),
        description="Cотрудники формы странины вакансий",
    )
    vacancy_about_1 = Field(VacancyAboutType, description='О компании')
    all_vacancies_category_1 = List(
        VacancyCategoryType1,
        description='Категории вакансий'
    )
    vacancy_should_work_1 = Field(
        VacancyShouldWorkType,
        description='Почему вам стоит работать'
    )
    all_vacancies_should_work_slider_1 = List(
        VacancyShouldWorkSliderType,
        description='Почему вам стоит работать ( слайдер )'
    )
    all_vacancies_slider_1 = List(
        VacancySliderType,
        description='Слайдер ( кадры нашей жизни )'
    )
    all_vacancies_employees_1 = List(
        VacancyEmployeesType,
        description='Сотрудники'
    )
    all_vacancies_desc_1 = List(
        VacancyDescriptionType,
        description='Описание вакансии'
    )

    @staticmethod
    def resolve_all_vacancies_category_1(obj, info, **kwargs):
        return query(VacancyCategory.objects.all(), info)

    @staticmethod
    def resolve_vacancy_about_1(obj, info, **kwargs):
        return VacancyAbout.get_solo()

    @staticmethod
    def resolve_vacancy_should_work_1(obj, info, **kwargs):
        return VacancyShouldWork.get_solo()

    @staticmethod
    def resolve_all_vacancies_should_work_slider_1(obj, info, **kwargs):
        return query(VacancyShouldWorkSlider.objects.all(), info)

    @staticmethod
    def resolve_all_vacancies_1(obj, info, **kwargs):
        return query(Vacancy.objects.filter(is_active=True).distinct(), info)

    @staticmethod
    def resolve_all_vacancies_slider_1(obj, info, **kwargs):
        return query(VacancySlider.objects.all(), info)

    @staticmethod
    def resolve_all_vacancies_employees_1(obj, info, **kwargs):
        return query(VacancyEmployees.objects.all(), info)

    @staticmethod
    def resolve_all_vacancies_desc_1(obj, info, **kwargs):
        # TODO: need fix
        return query(VacancyDescription.objects.all(), info)

    @staticmethod
    def resolve_vacancy_forms_employee_1(obj, info, **kwargs):
        qs = VacancyPageFormEmployee.objects.all()
        if kwargs.get("city"):
            try:
                _, city_id = from_global_id(kwargs.get("city"))
                return query(qs.filter(city=city_id), info)
            except (UnicodeDecodeError, BinasciiError, ValueError):
                return None
        return query(qs, info)

    @staticmethod
    def resolve_vacancies_1(obj, info, **kwargs):
        id = kwargs.get("id", None)
        if id:
            _, id = from_global_id(id)
            return (
                query(VacancyType1.get_queryset(Vacancy.objects.all(), info), info)
                .filter(id=id)
                .first()
            )
        return None
