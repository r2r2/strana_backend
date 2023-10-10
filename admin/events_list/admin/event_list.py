from http import HTTPStatus

import requests
from django.contrib import admin
from django.http import HttpResponseRedirect

from events_list.models import EventList, EventParticipantList
from solo.admin import SingletonModelAdmin


class EventParticipantListInLine(admin.StackedInline):
    model = EventParticipantList
    extra = 0
    classes = ['collapse']


@admin.register(EventList)
class EventListAdmin(SingletonModelAdmin):
    change_form_template = "events_list/templates/update_events_list.html"
    inlines = (EventParticipantListInLine,)
    search_fields = ("name", "event_date")
    list_display = (
        "name",
        "event_date",
    )

    def response_change(self, request, obj):
        if "_update" in request.POST:
            url = f'http://cabinet:1800/api/events_list/{obj.id}/update_event_participant_list/'
            response = requests.patch(url=url)
            if response.status_code == HTTPStatus.OK:
                self.message_user(request, "Данные списка участников были обновлены")
                return HttpResponseRedirect(".")
            else:
                self.message_user(request, "Не получилось обновить данные списка участников")
                return HttpResponseRedirect("../")
