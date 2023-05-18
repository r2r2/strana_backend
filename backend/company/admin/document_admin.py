from django.contrib.admin import register, ModelAdmin
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter
from ..models import Document


@register(Document)
class DocumentAdmin(ModelAdmin):
    list_display = ("title", "project", "category")
    list_filter = (("category", RelatedDropdownFilter), ("project", RelatedDropdownFilter))

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("project", "category")
