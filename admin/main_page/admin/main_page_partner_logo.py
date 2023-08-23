from django.contrib import admin

from ..models.main_page_partner_logo import MainPagePartnerLogo


@admin.register(MainPagePartnerLogo)
class MainPagePartnerLogoAdmin(admin.ModelAdmin):
    """
    Блок: Логотипы партнеров
    """
    list_display = (
        "id",
        "priority",
        "is_active",
    )
    ordering = ('-priority',)
    readonly_fields = ("created_at", "updated_at")
