from django.contrib import admin

from ..models import PurchaseAmoMatrix


@admin.register(PurchaseAmoMatrix)
class PurchaseAmoMatrixAdmin(admin.ModelAdmin):
    list_display = (
        "amo_payment_type",
        "payment_method",
        "mortgage_type",
        "default",
        "priority",
    )
    fieldsets = (
        (
            "Условия:", {
                "fields": (
                    "payment_method",
                    "mortgage_type",
                )
            }
        ),
        (
            "Результат:", {
                "fields": (
                    "amo_payment_type",
                )
            }
        ),
        (
            "Правила:", {
                "fields": (
                    "default",
                    "priority",
                )
            }
        )
    )
