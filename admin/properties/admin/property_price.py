from django.contrib import admin

from ..models import PropertyPrice, PropertyPriceType


@admin.register(PropertyPrice)
class PropertyPriceAdmin(admin.ModelAdmin):
    list_display = (
        "property",
        "price",
        "price_type",
    )
    search_fields = (
        "property__id",
        "property__article",
        "property__global_id",
    )
    list_filter = ("price_type__name",)


@admin.register(PropertyPriceType)
class PropertyPriceTypeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "default",
        "slug",
    )
