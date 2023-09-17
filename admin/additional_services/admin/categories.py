from django.contrib import admin

from ..models import AdditionalServiceCategory


@admin.register(AdditionalServiceCategory)
class AdditionalServiceCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "active",
        "priority",
    )
    search_fields = (
        "title",
    )
