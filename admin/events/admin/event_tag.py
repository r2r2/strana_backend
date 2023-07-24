from django.contrib import admin

from ..models import EventTag


@admin.register(EventTag)
class EventTagAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "color", "text_color")
