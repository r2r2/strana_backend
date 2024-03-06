from django.contrib import admin
from ..models import BookingEvent


@admin.register(BookingEvent)
class BookingEventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "event_name",
        "event_description",
        "slug",
    )
    list_display_links = (
        "id",
        "event_name",
    )


