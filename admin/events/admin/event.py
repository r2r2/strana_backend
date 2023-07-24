from common.loggers.models import BaseLogInline
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models import F, OuterRef, Subquery, When, Q, Case, BooleanField, Count

from ..models import Event, EventParticipant, EventParticipantStatus, EventTagThrough


class EventParticipantInline(BaseLogInline):
    model = EventParticipant
    readonly_fields = ('id',)
    autocomplete_fields = ("agent",)
    extra = 0


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    inlines = (EventParticipantInline,)
    list_filter = ("city", "type", "tags")
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
        "get_tags_on_list",
    )
    readonly_fields = ("participants_count", "has_empty_seats")

    def get_tags_on_list(self, obj):
        if obj.tags.exists():
            return [tag.name for tag in obj.tags.all()]
        else:
            return "-"

    get_tags_on_list.short_description = 'Теги мероприятий'
    get_tags_on_list.admin_order_field = 'event_tag'

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
        tag_qs = EventTagThrough.objects.filter(event__id=OuterRef("id"))

        qs = qs.annotate(
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
            event_tag=Subquery(tag_qs.values("tag__name")[:1]),
        )
        return qs
