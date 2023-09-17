from django.contrib import admin

from booking.models import BookingSource


@admin.register(BookingSource)
class BookingSourceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
    )
