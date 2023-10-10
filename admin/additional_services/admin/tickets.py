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
        "group_status",
        "service",
    )
    autocomplete_fields = (
        "service",
        "group_status",
        "booking",
        "user",
    )
