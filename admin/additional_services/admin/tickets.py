from django.contrib import admin

from ..models import AdditionalServiceTicket


@admin.register(AdditionalServiceTicket)
class AdditionalServiceTicketAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "full_name",
        "phone",
        "cost",
        "booking",
        "status",
        "service",
    )
    autocomplete_fields = (
        "service",
        "status",
        "booking",
    )
