from common.filters import FacetFilterSet
from ..models import AboutProjectGalleryCategory


class AboutProjectFilter(FacetFilterSet):
    class Meta:
        model = AboutProjectGalleryCategory
        fields = ("project",)
