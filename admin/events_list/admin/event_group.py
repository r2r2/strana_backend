from django.contrib import admin

from events_list.models import EventGroup
from events_list.models import EventParticipantList


@admin.register(EventGroup)
class EventGroupAdmin(admin.ModelAdmin):
    list_display = (
        "group_id",
        "timeslot",
        "event",
        "participant_count",
    )
    search_fields = (
        "group_id",
        "timeslot",
        "event__name",
    )

    def participant_count(self, inst):
        return EventParticipantList.objects.filter(group_id=inst.group_id).distinct().count()
