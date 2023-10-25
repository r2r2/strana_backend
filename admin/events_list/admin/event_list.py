from http import HTTPStatus

import requests
from django.contrib import admin
from django.http import HttpResponseRedirect

from events_list.models import EventList, EventParticipantList


class EventParticipantListInLine(admin.StackedInline):
    model = EventParticipantList
    extra = 0
    classes = ['collapse']


@admin.register(EventList)
class EventListAdmin(admin.ModelAdmin):
    change_form_template = "events_list/templates/update_events_list.html"
    inlines = (EventParticipantListInLine,)
    search_fields = ("name", "event_date")
    list_display = (
        "name",
        "event_id",
        "event_date",
    )

    def response_change(self, request, obj: EventList):
        if "_update" in request.POST:
            url = f'http://cabinet:1800/api/events_list/{obj.event_id}/update_event_participant_list/'
            response = requests.patch(url=url)
            if response.status_code == HTTPStatus.OK:
                self.message_user(request, "Данные списка участников были обновлены")
                return HttpResponseRedirect(".")
            else:
                error_response: list[bytes] = list(response.iter_lines())
                error_msg: str = (f"Не получилось обновить данные списка участников: "
                                  f"{error_response[-3:]}")
                self.message_user(request, error_msg)
                return HttpResponseRedirect("../")
        return super().response_change(request, obj)
