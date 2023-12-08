from django.contrib import admin

from mortgage.models import MortgageTicket

@admin.register(MortgageTicket)
class MortgageTicketAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_at",
    )
    search_fields = (
        "id",
    )
