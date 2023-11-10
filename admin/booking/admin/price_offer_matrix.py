from django.contrib import admin

from ..models import PriceOfferMatrix


@admin.register(PriceOfferMatrix)
class PriceOfferMatrixAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "payment_method",
        "price_type",
        "by_dev",
        "priority",
    )
    fieldsets = (
        (
            "Условия:", {
                "fields": (
                    "name",
                    "payment_method",
                    "mortgage_type",
                    "by_dev",
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
