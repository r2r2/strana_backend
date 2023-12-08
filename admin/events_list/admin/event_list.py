from http import HTTPStatus

import requests
from django.contrib import admin
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseRedirect
from requests import Response

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
        "get_inline_count",
    )

    def response_change(self, request: WSGIRequest, obj: EventList):
        if "_update" in request.POST:
            url: str = f'http://cabinet:1800/api/events_list/{obj.event_id}/update_event_participant_list/'
            response = requests.patch(url=url)
            self._process_response(
                response=response,
                request=request,
                success_msg="Данные списка участников были обновлены",
                error_msg="Не получилось обновить данные списка участников:"
            )
        elif "_delete" in request.POST:
            url: str = f'http://cabinet:1800/api/events_list/{obj.event_id}/delete_event_participant_list/'
            response: Response = requests.delete(url=url)
            self._process_response(
                response=response,
                request=request,
                success_msg="Данные списка участников были удалены",
                error_msg="Не получилось удалить данные списка участников:"
            )
        return super().response_change(request, obj)

    def get_inline_count(self, obj):
        inline_model = EventParticipantList
        filter_field = 'event_id'
        count = inline_model.objects.filter(**{filter_field: obj.id}).count()
        return count

    get_inline_count.short_description = 'Количество участников'

    def _process_response(
        self,
        response: Response,
        request: WSGIRequest,
        success_msg: str,
        error_msg: str
    ) -> HttpResponseRedirect:
        if response.status_code == HTTPStatus.OK:
            self.message_user(request, success_msg)
            return HttpResponseRedirect(".")
        else:
            error_response: list[bytes] = list(response.iter_lines())
            error_msg: str = f"{error_msg} {error_response[-3:]}"
            self.message_user(request, error_msg)
            return HttpResponseRedirect("../")
