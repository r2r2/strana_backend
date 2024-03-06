from django.contrib.admin import register, ModelAdmin

from ..models import DocumentArchive


@register(DocumentArchive)
class DocumentArchiveAdmin(ModelAdmin):
    list_display = (
        "id",
        "slug"
    )
    list_display_links = (
        "id",
        "slug"
    )
