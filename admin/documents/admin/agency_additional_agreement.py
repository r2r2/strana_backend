from django.contrib import admin
from django.utils.html import mark_safe

from ..models import AgencyAdditionalAgreement


@admin.register(AgencyAdditionalAgreement)
class AgencyAdditionalAgreementAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "template_name",
        "agency",
        "booking",
        "project",
        "signed_at",
        "status",
        "reason_comment",
    )
    autocomplete_fields = (
        "project",
        "booking",
        "agency",
    )
    search_fields = (
        "template_name",
        "agency__name",
        "agency__inn",
        "agency__amocrm_id",
        "booking__amocrm_id",
        "booking__id",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "files",
        "download_file",
        "signed_at",
        "creating_data",
    )
    list_filter = ("creating_data",)

    def download_file(self, instance):
        if instance.files:
            if file_link := instance.files[0].get("files")[0].get("aws"):
                return mark_safe(f'<a class="grp-button" href={file_link} target="blank">Ссылка на файл</a>')
        else:
            return "-"

    download_file.short_description = "Скачать файл"
