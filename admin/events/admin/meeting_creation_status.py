from django.contrib import admin

from ..models import MeetingCreationSource


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
