from django.db.models import Prefetch
from django_filters import BaseInFilter

from common.filters import FacetFilterSet
from infras.models import InfraCategory, Infra


class InfraCategoryFilterSet(FacetFilterSet):
    project = BaseInFilter(
        field_name="infratype__infra__project_id", label="project_id", method="project_filter"
    )

    class Meta:
        model = InfraCategory
        fields = ("project",)

    @staticmethod
    def project_filter(queryset, name, value):
        queryset = queryset.prefetch_related(None)
        queryset = queryset.prefetch_related(
            Prefetch(
                "infratype_set__infra_set",
                Infra.objects.filter(project=value[0]).prefetch_related("infracontent_set"),
            )
        )
        return queryset
