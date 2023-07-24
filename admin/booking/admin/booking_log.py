from django.contrib import admin
from ..models import BookingLog


@admin.register(BookingLog)
class BookingLogAdmin(admin.ModelAdmin):
    search_fields = ("booking__amocrm_id", "booking__id")
    list_display = (
        "booking",
        "created",
        "state_difference",
        "content",
        "use_case",
    )
