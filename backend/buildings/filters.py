from django_filters import FilterSet, MultipleChoiceFilter, NumberFilter
from graphene_django.filter import GlobalIDFilter, GlobalIDMultipleChoiceFilter
from .constants import BuildingType
from .models import Building, Floor


class BuildingFilterSet(FilterSet):
    """
    Фильтр корпусов
    """

    kind = MultipleChoiceFilter(
        field_name="kind", choices=BuildingType.choices, label="Фильтр по виду"
    )
    project = GlobalIDFilter(field_name="project__slug", label="Фильтр по проекту")

    class Meta:
        model = Building
        fields = ("project", "kind")


class FloorFilterSet(FilterSet):
    """ Фильтр этажей """

    id = GlobalIDFilter(field_name="id", label="Фильтр по ID")
    section = GlobalIDFilter(field_name="section", label="Фильтр по секции")
    building = GlobalIDFilter(field_name="section__building", label="Фильтр по корпусу")

    class Meta:
        model = Floor
        fields = ()
