from django.contrib import admin

from ..models.main_page_offer import MainPageOffer


@admin.register(MainPageOffer)
class MainPageOfferAdmin(admin.ModelAdmin):
    """
    Блок: Что мы предлагаем
    """
    list_display = (
        "title",
        "description",
        "priority",
        "is_active",
    )
    ordering = ('-priority',)
    readonly_fields = ("created_at", "updated_at")
