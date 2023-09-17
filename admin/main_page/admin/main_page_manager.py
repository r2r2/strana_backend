from django.contrib import admin

from ..models.main_page_manager import MainPageManager


@admin.register(MainPageManager)
class MainPageManagerAdmin(admin.ModelAdmin):
    """
    Блок: Контакты менеджера
    """
    list_display = (
        "id",
        "manager",
        "position",
    )
