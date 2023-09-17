from django.contrib import admin

from ..models import Floor

@admin.register(Floor)
class FloorAdmin(admin.ModelAdmin):
    search_fields = (
        "number",
        "building__name",
        "building__project__name",
        "global_id",
    )
    autocomplete_fields = (
        "building",
    )
    list_display = ("global_id", "building", "number")
