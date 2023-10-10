from django.contrib import admin

from ..models import AddServiceSettings


@admin.register(AddServiceSettings)
class AddServiceSettingsAdmin(admin.ModelAdmin):
    """
    Настройки доп. услуг
    """

    list_display = (
        "id",
        "email",
    )
    list_editable = ("email",)
    search_fields = ("email",)
