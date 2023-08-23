from django.contrib import admin

from ..models import MeetingStatus


@admin.register(MeetingStatus)
class MeetingStatusAdmin(admin.ModelAdmin):
    list_display = (
        "sort",
        "label",
        "slug",
        "is_final",
    )
    search_fields = (
        "slug",
        "label",
        "sort",
    )
