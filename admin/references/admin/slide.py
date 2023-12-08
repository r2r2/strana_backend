from django.contrib import admin

from ..models import Slide


@admin.register(Slide)
class SlideAdmin(admin.ModelAdmin):
    list_display = ("is_active", "priority", "title", "subtitle", "desktop_media", "tablet_media", "mobile_media")
    ordering = ["priority"]