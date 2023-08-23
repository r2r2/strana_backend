from common.loggers.models import BaseLogInline
from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models import (BooleanField, Case, Count, Exists, F, OuterRef,
                              Q, Subquery, When)

from ..models import (CalendarEvent, CalendarEventTagThrough,
                      CalendarEventType, Event, EventParticipant,
                      EventParticipantStatus)


class CalendarEventAdminForm(forms.ModelForm):
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


class CalendarEventInline(BaseLogInline):
    form = CalendarEventAdminForm
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


class EventParticipantInline(BaseLogInline):
    model = EventParticipant
    readonly_fields = ("id", "fio", "phone")
    autocomplete_fields = ("agent",)
    extra = 0


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    inlines = (EventParticipantInline, CalendarEventInline)
    actions = ("add_calendar_events",)
    list_filter = ("city", "type", "calendar_event__tags")
    search_fields = ("city__name", "name", "description", "manager_fio", "manager_phone")
    list_display = (
        "id",
        "name",
        "type",
        "meeting_date_start",
        "meeting_date_end",
        "has_empty_seats",
        "participants_count",
        "is_active",
        "has_calendar_event",
        "get_calendar_tags_on_list",
    )
    readonly_fields = ("participants_count", "has_empty_seats")

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

    def has_empty_seats(self, obj):
        return obj.has_empty_seats

    has_empty_seats.short_description = "Статус записи на мероприятие"
    has_empty_seats.admin_order_field = 'has_empty_seats'
    has_empty_seats.boolean = True

    def participants_count(self, obj):
        return obj.participants_count

    participants_count.short_description = "Всего участвует агентов"
    participants_count.admin_order_field = 'participants_count'

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

    def get_queryset(self, request):
        qs = super(EventAdmin, self).get_queryset(request)
        participants_qs = EventParticipant.objects.filter(
            event__id=OuterRef("id"),
            status=EventParticipantStatus.RECORDED,
        ).values('event__id').annotate(count=Count('pk')).values('count')
        has_calendar_event_qs = CalendarEvent.objects.filter(event__id=OuterRef("id"))
        calendar_tag_qs = CalendarEventTagThrough.objects.filter(calendar_event__id=OuterRef("calendar_event__id"))

        qs = qs.annotate(
            has_calendar_event=Exists(has_calendar_event_qs),
            calendar_event_tag=Subquery(calendar_tag_qs.values("tag__label")[:1]),
            participants_count=Subquery(participants_qs),
            has_empty_seats=Case(
                When(
                    Q(max_participants_number__gt=0)
                    & Q(participants_count__gte=F("max_participants_number")),
                    then=False,
                ),
                default=True,
                output_field=BooleanField(),
            ),
        )
        return qs

    def add_calendar_events(self, request, queryset):
        calendar_events_data = []
        for event in queryset:
            if not event.has_calendar_event:
                calendar_events_data.append(
                    CalendarEvent(
                        title=event.name,
                        type=CalendarEventType.EVENT,
                        format_type=event.type,
                        date_start=event.meeting_date_start,
                        date_end=event.meeting_date_end,
                        event=event,
                    )
                )
        CalendarEvent.objects.bulk_create(calendar_events_data)

    add_calendar_events.short_description = "Добавить события календаря"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:
            calendar_event = CalendarEvent(
                title=obj.name,
                type=CalendarEventType.EVENT,
                format_type=obj.type,
                date_start=obj.meeting_date_start,
                date_end=obj.meeting_date_end,
                event=obj,
            )
            calendar_event.save()
        elif obj.has_calendar_event:
            obj.calendar_event.save()
