from django.contrib import admin

from .models import FAQ, FAQPageType


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "slug",
        "question",
        "is_active",
        "order",
    )
    list_filter = (
        "is_active",
    )
    list_display_links = (
        "slug",
        "question",
    )
    ordering = ("order",)


@admin.register(FAQPageType)
class FAQPageTypeAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "slug",
    )
