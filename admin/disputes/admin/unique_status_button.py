from django.contrib.admin import register, ModelAdmin

from disputes.models import UniqueStatusButton


@register(UniqueStatusButton)
class UniqueStatusButtonAdmin(ModelAdmin):
    list_display = (
        "text",
        "slug",
        "background_color",
        "text_color",
        "description",
    )
