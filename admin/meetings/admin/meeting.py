from django.contrib import admin
from meetings.models import Meeting


@admin.register(Meeting)
class MeetingsAdmin(admin.ModelAdmin):
    list_display = (
        "topic",
        "booking",
        "user_phone",
        "user_amocrm_id",
        "booking_amocrm_id",
        "city",
        "project",
        "local_date",
    )
    readonly_fields = (
        "local_date",
    )
    exclude = (
        "date",
    )
    autocomplete_fields = ("booking",)
    search_fields = (
        "booking__user__phone__icontains",
        "booking__user__amocrm_id__icontains",
        "booking__amocrm_id__icontains",
    )

    def local_date(self, obj):
        return obj.date.strftime("%d-%m-%Y %H:%M") if obj.date else "-"

    local_date.short_description = "Дата встречи по местному времени"
    local_date.admin_order_field = 'date'

    def user_phone(self, obj):
        return obj.booking.user.phone if (obj.booking and obj.booking.user) else "-"

    user_phone.short_description = "Телефон клиента"
    user_phone.admin_order_field = 'booking__user__phone'

    def user_amocrm_id(self, obj):
        return obj.booking.user.amocrm_id if (obj.booking and obj.booking.user) else "-"

    user_amocrm_id.short_description = "Амосрм ID клиента"
    user_amocrm_id.admin_order_field = 'booking__user__amocrm_id'

    def booking_amocrm_id(self, obj):
        return obj.booking.amocrm_id if obj.booking else "-"

    user_phone.short_description = "Амосрм ID сделки"
    user_phone.admin_order_field = 'booking__amocrm_id'
