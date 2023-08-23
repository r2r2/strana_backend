from django.contrib import admin

from ..models.main_page_sell_online import MainPageSellOnline


@admin.register(MainPageSellOnline)
class MainPageSellOnlineAdmin(admin.ModelAdmin):
    """
    Блок: Продавайте online
    """
    list_display = (
        "id",
        "title",
        "priority",
        "is_active",
    )
    ordering = ('-priority',)
    readonly_fields = ("created_at", "updated_at")
