from django.contrib import admin

from ..models import Cities


@admin.register(Cities)
class CitiesAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "phone",
        "timezone_offset",
    )
    search_fields = ("name", )
