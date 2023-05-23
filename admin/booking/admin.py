import os
import urllib.parse

import requests
from django.contrib import admin

from common.loggers.models import BaseLogInline
from .exceptions import InvalidURLException, ConnectCabinetError
from .models import Booking, BookingHelpText, BookingLog


class BookingLogInline(BaseLogInline):
    model = BookingLog


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    inlines = (BookingLogInline, )
    search_fields = (
        "amocrm_id__icontains",
        "user__phone__icontains",
        "user__name__icontains",
        "user__surname__icontains",
        "agent__name__icontains",
        "agent__surname__icontains",
        "agent__phone__icontains",
        "agency__name__icontains",
        "id",
    )
    list_display = (
        "__str__",
        "active",
        "completed",
        "expired",
        "overed",
        "user",
        "agent",
        "agency",
        "amocrm_id",
        "errors",
    )
    save_on_top = True
    list_per_page = 15
    show_full_result_count = False
    list_select_related = True

    def save_model(self, request, obj, form, change):
        booking_before_save = Booking.objects.get(id=obj.id)
        super().save_model(request, obj, form, change)
        old_status = booking_before_save.amocrm_status_id
        new_status = obj.amocrm_status_id
        if old_status != new_status:
            url = f'http://cabinet:1800/api/task_management/admin/create_task_instance/{obj.id}/'

            # Parse the URL and check whether it is valid
            parsed_url = urllib.parse.urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise InvalidURLException(f"Invalid URL: {url}")
            try:
                requests.post(url)
            except requests.exceptions.ConnectionError as e:
                raise ConnectCabinetError(f"Can't connect to cabinet: {e}")


@admin.register(BookingHelpText)
class BookingHelpTextAdmin(admin.ModelAdmin):
    list_display = (
        "booking_online_purchase_step",
        "payment_method",
        "maternal_capital",
        "certificate",
        "loan",
        "default",
    )


@admin.register(BookingLog)
class BookingLogAdmin(admin.ModelAdmin):
    search_fields = ("booking__amocrm_id", )
    list_display = (
        "amocrm_id",
        "created",
        "state_difference",
    )

    def amocrm_id(self, obj):
        return obj.booking.amocrm_id
