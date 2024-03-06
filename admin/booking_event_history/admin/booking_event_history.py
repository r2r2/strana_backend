from django.contrib import admin
from ..models import BookingEventHistory


@admin.register(BookingEventHistory)
class BookingEventHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "actor",
        "event_slug",
        "date_time",
        "event_name",
    )
    autocomplete_fields = (
        "booking",
    )
    list_filter = (
        "date_time",
        "event"
    )
    search_fields = (
        "actor",
        "booking__user__phone__icontains",
        "booking__user__amocrm_id__icontains",
        "booking__amocrm_id__icontains",
        "booking__pk__icontains",
    )
