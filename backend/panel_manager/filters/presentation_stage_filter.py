from django_filters import BaseInFilter

from common.filters import FacetFilterSet
from ..models import PresentationStage, AboutProjectGalleryCategory


class PresentationStageFilter(FacetFilterSet):
    project = BaseInFilter(label="Проект", method="project_filter")

    class Meta:
        model = PresentationStage
        fields = ("hard_type", "project")

    def project_filter(self, qs, name, values):
        apg = set(
            AboutProjectGalleryCategory.objects.filter(project_id__in=values).values_list(
                "aboutprojectgallerycategory_rm", flat=True
            )
        )
        qs = qs.filter(id__in=apg)
        return qs
