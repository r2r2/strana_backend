from django.contrib import admin

from ..models import AgencyAgreement
from .agency_act import AgencyActAdmin


@admin.register(AgencyAgreement)
class AgencyAgreementAdmin(AgencyActAdmin):
    list_display = (
        "id",
        "template_name",
        "agency",
        "booking",
        "project",
        "agreement_type",
        "signed_at",
        "status",
    )
    search_fields = (
        "template_name",
        "agency__name",
        "agency__inn",
        "agency__amocrm_id",
        "project__name",
        "booking__amocrm_id",
        "booking__id",
    )
    autocomplete_fields = (
        "project",
        "booking",
        "agency",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
        "files",
        "download_file",
        "signed_at",
    )
