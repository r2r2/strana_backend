from django.contrib import admin

from ..models import Building


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    search_fields = ("name", "project__name")
    list_display = ("name", "project", "global_id")
