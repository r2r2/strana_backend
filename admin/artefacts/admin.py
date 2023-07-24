from django.contrib import admin
from .models import CheckUnique, ShowtimeRegistration, Document, Escrow, BookingHelpText, Tip


@admin.register(CheckUnique)
class CheckUniqueAdmin(admin.ModelAdmin):
    pass


@admin.register(ShowtimeRegistration)
class ShowtimeRegistrationAdmin(admin.ModelAdmin):
    pass


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    pass


@admin.register(Escrow)
class EscrowAdmin(admin.ModelAdmin):
    list_display = ("slug", "file")


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


@admin.register(Tip)
class TipsAppConfig(admin.ModelAdmin):
    pass
