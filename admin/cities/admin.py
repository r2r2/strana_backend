from django.contrib import admin

from cities.models import Cities


@admin.register(Cities)
class CitiesAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
    )
