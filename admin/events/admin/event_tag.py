from django.contrib import admin

from ..models import EventTag


@admin.register(EventTag)
class EventTagAdmin(admin.ModelAdmin):
    list_display = ("id", "label", "color", "background_color")
