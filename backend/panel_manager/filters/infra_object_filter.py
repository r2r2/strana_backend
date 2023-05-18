from django_filters import BaseInFilter

from common.filters import FacetFilterSet
from infras.models import Infra


class InfraObjectFilterSet(FacetFilterSet):
    project = BaseInFilter(field_name="project_id", label="project")

    class Meta:
        model = Infra
        fields = ("project",)
