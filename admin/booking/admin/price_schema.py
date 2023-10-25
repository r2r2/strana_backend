from django.contrib import admin

from ..models import PriceSchema


@admin.register(PriceSchema)
class PriceSchemaAdmin(admin.ModelAdmin):
    list_display = (
        "price_type",
        "slug",
    )
