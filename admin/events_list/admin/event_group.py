from django.contrib import admin

from events_list.models import EventGroup


@admin.register(EventGroup)
class EventGroupAdmin(admin.ModelAdmin):
    list_display = (
        "group_id",
        "timeslot",
        "event",
    )
    search_fields = (
        "group_id",
        "timeslot",
        "event__name",
    )

