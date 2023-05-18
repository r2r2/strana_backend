from django_filters import CharFilter, BooleanFilter
from graphene_django.filter import GlobalIDFilter
from graphene_django.filter.filterset import GrapheneFilterSetMixin, GlobalIDMultipleChoiceFilter
from .models import Vacancy
from common.filters import FacetFilterSet


class VacancyFilterSet(GrapheneFilterSetMixin, FacetFilterSet):
    """
    Фильтр вакансий
    """

    city = GlobalIDFilter(field_name="city", label="Фильтр по городу")
    category = GlobalIDFilter(field_name="category", label="Фильтр по категории")
    text = CharFilter(field_name="job_title", lookup_expr="icontains", label="Фильтр по названию")

    class Meta:
        model = Vacancy
        fields = ("city", "category", "text")
