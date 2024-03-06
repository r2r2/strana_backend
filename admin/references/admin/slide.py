from django.contrib import admin

from ..models import Slide


@admin.register(Slide)
class SlideAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "priority", "subtitle", "desktop_media", "tablet_media", "mobile_media")
    list_display_links = ("title", )
    ordering = ["priority"]
