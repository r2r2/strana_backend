from django.contrib import admin

from ..models import PropertyPrice, PropertyPriceType


@admin.register(PropertyPrice)
class PropertyPriceAdmin(admin.ModelAdmin):
    list_display = (
        "price",
        "price_type",
    )


@admin.register(PropertyPriceType)
class PropertyPriceTypeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "default",
        "slug",
    )
