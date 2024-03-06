from django.contrib import admin

from ..models import MeetingStatus, MeetingStatusRef


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


@admin.register(MeetingStatusRef)
class MeetingStatusRefAdmin(admin.ModelAdmin):
    list_display = (
        "label",
        "slug",
        "sort",
        "is_final",
    )
    search_fields = (
        "slug",
        "label",
        "sort",
    )
