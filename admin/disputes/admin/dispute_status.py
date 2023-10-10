from django.contrib.admin import register, ModelAdmin

from ..models import DisputeStatus


@register(DisputeStatus)
class DisputeStatusAdmin(ModelAdmin):
    list_display = (
        "title",
    )
