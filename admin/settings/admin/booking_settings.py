from django.contrib import admin

from settings.models.booking_settings import BookingSettings


@admin.register(BookingSettings)
class BookingSettingsAdmin(admin.ModelAdmin):
    """
    Настройки бронирования
    """
    list_display = (
        'id',
        'name',
        'default_flats_reserv_time',
    )
    list_editable = (
        'default_flats_reserv_time',
    )
    search_fields = (
        'id',
        'name',
    )
    readonly_fields = ("created_at", "updated_at")
