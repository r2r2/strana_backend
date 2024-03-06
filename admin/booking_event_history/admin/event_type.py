from django.contrib import admin
from ..models import EventType


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "event_type_name",
        "slug",
    )
    list_display_links = (
        "id",
        "event_type_name"
    )

