from django.contrib import admin
from meetings.models import Meeting


@admin.register(Meeting)
class MeetingsAdmin(admin.ModelAdmin):
    list_display = (
        "topic",
        "booking",
        "city",
        "project",
        "local_date",
    )
    readonly_fields = (
        "local_date",
    )
    exclude = (
        "date",
    )

    def local_date(self, obj):
        return obj.date.strftime("%d-%m-%Y %H:%M")

    local_date.short_description = "Дата встречи по местному времени"
