from django.contrib import admin

from ..models import PriceOfferMatrix


@admin.register(PriceOfferMatrix)
class PriceOfferMatrixAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "payment_method",
        "mortgage_type",
        "price_type",
        "default",
        "priority",
    )
    fieldsets = (
        (
            "Условия:", {
                "fields": (
                    "name",
                    "payment_method",
                    "mortgage_type",
                    "default",
                )
            }
        ),
        (
            "Результат:", {
                "fields": (
                    "price_type",
                    "priority",
                )
            }
        )
    )
