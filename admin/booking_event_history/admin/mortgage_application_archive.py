from django.contrib import admin
from ..models import MortgageApplicationArchive


@admin.register(MortgageApplicationArchive)
class MortgageApplicationArchiveAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "external_code",
        "booking_id",
        "mortgage_application_status_until",
        "mortgage_application_status_after",
        "status_change_date",
    )
    list_display_links = (
        "id",
    )
