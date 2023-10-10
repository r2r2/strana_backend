from django.contrib import admin

from ..models import AdditionalService


@admin.register(AdditionalService)
class AdditionalServiceAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "announcement",
        "condition",
        "category",
        "priority",
    )
    search_fields = (
        "title",
        "announcement",
        "description",
    )
    autocomplete_fields = (
        "condition",
        "category",
    )
