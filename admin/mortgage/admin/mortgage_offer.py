from django.contrib import admin

from mortgage.models import MortgageOffer


@admin.register(MortgageOffer)
class MortgageOfferAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "bank",
        "program",
        "external_code",
        "credit_term",
        "uid",
    )
    search_fields = (
        "id",
        "name",
        "bank",
        "program",
        "external_code",
    )
