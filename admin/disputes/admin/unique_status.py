from django.contrib.admin import register, ModelAdmin

from ..models import UniqueStatus


@register(UniqueStatus)
class UniqueStatusAdmin(ModelAdmin):
    list_display = (
        "title",
        "subtitle",
        "slug",
        "type",
        "comment",
    )
