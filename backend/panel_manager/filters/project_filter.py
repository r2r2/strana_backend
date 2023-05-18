from django_filters.rest_framework import BooleanFilter

from common.filters import FacetFilterSet, NumberInFilter
from projects.models import Project


class ProjectFilter(FacetFilterSet):
    show_in_panel_manager = BooleanFilter(label="Показывать на панели менеджера")
    show_in_panel_manager.skip = True

    class Meta:
        model = Project
        fields = ("show_in_panel_manager", "status")
