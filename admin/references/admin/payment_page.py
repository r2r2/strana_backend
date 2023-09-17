from django.contrib import admin

from ..models import PaymentPageNotification


@admin.register(PaymentPageNotification)
class PaymentPageNotificationAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "notify_text",
        "button_text",
    )
