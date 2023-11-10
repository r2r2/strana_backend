from django.contrib import admin

from settings.models import SystemList


@admin.register(SystemList)
class SystemListAdmin(admin.ModelAdmin):
    """
    Список систем
    """
    list_display = (
        'id',
        'name',
        'slug',
    )
    search_fields = (
        'id',
        'name',
        'slug',
    )
