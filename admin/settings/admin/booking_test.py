from django.contrib import admin

from settings.models.booking_test import TestBooking


@admin.register(TestBooking)
class TestBookingAdmin(admin.ModelAdmin):
    """
    Тестовые сделки
    """
    list_display = (
        'amocrm_id',
        'id',
        'booking',
        'status',
        "last_check_at",
        "is_check_skipped",
        'info',
        "created_at",
    )
    list_editable = ("is_check_skipped",)
    autocomplete_fields = ("booking",)
    readonly_fields = ("created_at", "updated_at")
