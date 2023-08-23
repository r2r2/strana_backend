from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse

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

    def changelist_view(self, request, extra_context=None):
        if BookingSettings.objects.exists():
            obj = BookingSettings.objects.first()
            return HttpResponseRedirect(
                reverse(f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change', args=[obj.pk])
            )
        return super().changelist_view(request, extra_context)
