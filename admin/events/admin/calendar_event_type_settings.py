from django.contrib import admin

from ..models import CalendarEventTypeSettings


@admin.register(CalendarEventTypeSettings)
class CalendarEventTypeSettingsAdmin(admin.ModelAdmin):
    list_filter = ("type",)
    list_display = (
        "type",
        "color",
    )
