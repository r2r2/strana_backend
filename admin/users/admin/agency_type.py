from django.contrib import admin

from ..models import AgencyGeneralType


@admin.register(AgencyGeneralType)
class AgencyGeneralTypeAdmin(admin.ModelAdmin):
    list_display = (
        "sort",
        "label",
        "slug",
    )
    search_fields = (
        "slug",
        "label",
    )
