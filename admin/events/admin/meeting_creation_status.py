from django.contrib import admin

from ..models import MeetingCreationSource
from ..models import MeetingCreationSourceRef


# deprecated
@admin.register(MeetingCreationSource)
class MeetingCreationSourceAdmin(admin.ModelAdmin):
    list_display = (
        "label",
        "slug",
    )
    search_fields = (
        "label",
        "slug",
    )


@admin.register(MeetingCreationSourceRef)
class MeetingCreationSourceRefAdmin(admin.ModelAdmin):
    list_display = (
        "label",
        "slug",
    )
    search_fields = (
        "label",
        "slug",
    )
