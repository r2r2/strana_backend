from common.loggers.models import BaseLogInline
from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models import Exists, OuterRef, Subquery

from ..models import (CalendarEvent, CalendarEventTagThrough,
                      CalendarEventType, Meeting)


class CalendarMeetingAdminForm(forms.ModelForm):
    class Meta:
        model = CalendarEvent
        fields = [
            "title",
            "type",
            "format_type",
            "date_start",
            "date_end",
            "tags",
        ]


class CalendarMeetingInline(BaseLogInline):
    form = CalendarMeetingAdminForm
    model = CalendarEvent
    readonly_fields = [
        "title",
        "type",
        "format_type",
        "date_start",
        "date_end",
    ]
    extra = 0

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "tags":
            kwargs['widget'] = FilteredSelectMultiple(
                db_field.verbose_name,
                is_stacked=False,
            )
        else:
            return super().formfield_for_manytomany(db_field, request, **kwargs)
        form_field = db_field.formfield(**kwargs)
        msg = "Зажмите 'Ctrl' ('Cmd') или проведите мышкой, с зажатой левой кнопкой, чтобы выбрать несколько элементов."
        form_field.help_text = msg
        return form_field


@admin.register(Meeting)
class MeetingsAdmin(admin.ModelAdmin):
    inlines = (CalendarMeetingInline,)
    actions = ("add_calendar_events",)
    list_display = (
        "topic",
        "booking",
        "user_phone",
        "user_amocrm_id",
        "booking_amocrm_id",
        "city",
        "project",
        "local_date",
        "has_calendar_event",
        "get_calendar_tags_on_list",
    )
    readonly_fields = (
        "local_date",
        "date",
        "city",
        "project",
        "booking",
        "status",
        "record_link",
        "meeting_link",
        "meeting_address",
        "topic",
        "type",
        "property_type",
    )
    exclude = (
        "date",
    )
    autocomplete_fields = ("booking",)
    search_fields = (
        "booking__user__phone__icontains",
        "booking__user__amocrm_id__icontains",
        "booking__amocrm_id__icontains",
    )
    list_filter = ("calendar_event__tags",)

    def has_calendar_event(self, obj):
        return obj.has_calendar_event

    has_calendar_event.short_description = "В календаре"
    has_calendar_event.admin_order_field = 'has_calendar_event'
    has_calendar_event.boolean = True

    def get_calendar_tags_on_list(self, obj):
        if obj.calendar_event and obj.calendar_event.tags.exists():
            return [tag.label for tag in obj.calendar_event.tags.all()]
        else:
            return "-"

    get_calendar_tags_on_list.short_description = 'Теги события календаря'
    get_calendar_tags_on_list.admin_order_field = 'calendar_event_tag'

    def local_date(self, obj):
        return obj.date.strftime("%d-%m-%Y %H:%M") if obj.date else "-"

    local_date.short_description = "Дата встречи по местному времени"
    local_date.admin_order_field = 'date'

    def user_phone(self, obj):
        return obj.booking.user.phone if (obj.booking and obj.booking.user) else "-"

    user_phone.short_description = "Телефон клиента"
    user_phone.admin_order_field = 'booking__user__phone'

    def user_amocrm_id(self, obj):
        return obj.booking.user.amocrm_id if (obj.booking and obj.booking.user) else "-"

    user_amocrm_id.short_description = "Амосрм ID клиента"
    user_amocrm_id.admin_order_field = 'booking__user__amocrm_id'

    def booking_amocrm_id(self, obj):
        return obj.booking.amocrm_id if obj.booking else "-"

    booking_amocrm_id.short_description = "Амосрм ID сделки"
    booking_amocrm_id.admin_order_field = 'booking__amocrm_id'

    def get_queryset(self, request):
        qs = super(MeetingsAdmin, self).get_queryset(request)
        has_calendar_event_qs = CalendarEvent.objects.filter(meeting__id=OuterRef("id"))
        calendar_tag_qs = CalendarEventTagThrough.objects.filter(calendar_event__id=OuterRef("calendar_event__id"))

        qs = qs.annotate(
            has_calendar_event=Exists(has_calendar_event_qs),
            calendar_event_tag=Subquery(calendar_tag_qs.values("tag__label")[:1]),
        )
        return qs

    def add_calendar_events(self, request, queryset):
        calendar_events_data = []
        for meeting in queryset:
            if not meeting.has_calendar_event:
                if meeting.type == "kc":
                    format_type = "online"
                else:
                    format_type = "offline"
                calendar_events_data.append(
                    CalendarEvent(
                        type=CalendarEventType.MEETING,
                        format_type=format_type,
                        date_start=meeting.date,
                        meeting=meeting,
                    )
                )
        CalendarEvent.objects.bulk_create(calendar_events_data)

    add_calendar_events.short_description = "Добавить события календаря"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.has_calendar_event:
            obj.calendar_event.save()
