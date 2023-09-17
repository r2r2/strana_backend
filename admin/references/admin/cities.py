from django.contrib import admin

from ..models import Cities


@admin.register(Cities)
class CitiesAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "phone"
    )
    search_fields = ("name", )
