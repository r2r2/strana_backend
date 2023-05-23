from common.loggers.models import BaseLogInline
from django.contrib import admin
from django.utils.html import mark_safe

from .models import Agency, AgencyAct, AgencyAgreement, AgencyLog, AgencyAdditionalAgreement


class AgencyLogInline(BaseLogInline):
    model = AgencyLog


@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at",)
    list_display = (
        "name",
        "is_approved",
        "is_deleted",
        "created_at",
    )
    inlines = (AgencyLogInline, )


@admin.register(AgencyAct)
class AgencyActAdmin(admin.ModelAdmin):
    list_display = ("__str__", "template_name", "agency", "project", "booking",
                    "signed_at", "status", "get_agent_on_list")
    readonly_fields = (
        "agent",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
        "files",
        "download_file",
        "signed_at",
    )
    search_fields = ("template_name", "agency__name", "agency__inn", "project__name", "booking__agent__name",
                     "booking__agent__surname", "booking__agent__patronymic", "booking__agent__amocrm_id",
                     "status__name")

    def get_agent_on_list(self, obj):
        if obj.booking and obj.booking.agent:
            return f"{obj.booking.agent.amocrm_id} {obj.booking.agent.full_name()}"
        else:
            return "-"

    get_agent_on_list.short_description = 'Ответственный агент'

    def agent(self, instance):
        if instance.booking and instance.booking.agent:
            return instance.booking.agent
        else:
            return "-"

    agent.short_description = "Ответственный агент"

    def download_file(self, instance):
        if instance.files:
            if file_link := instance.files[0].get("files")[0].get("aws"):
                return mark_safe(f'<a class="grp-button" href={file_link} target="blank">Ссылка на файл</a>')
        else:
            return "-"

    download_file.short_description = "Скачать файл"

    def save_model(self, request, obj, form, change):
        obj.updated_by_id = request.user.id
        super().save_model(request, obj, form, change)


@admin.register(AgencyAgreement)
class AgencyAgreementAdmin(AgencyActAdmin):
    list_display = ("__str__", "template_name", "agency", "project", "agreement_type", "signed_at", "status")
    search_fields = ("template_name", "agency__name", "agency__inn", "project__name")
    readonly_fields = (
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
        "files",
        "download_file",
        "signed_at",
    )


@admin.register(AgencyAdditionalAgreement)
class AgencyAdditionalAgreementAdmin(admin.ModelAdmin):
    list_display = ("__str__", "template_name", "agency", "project", "signed_at", "status")
    readonly_fields = (
        "created_at",
        "updated_at",
        "files",
        "download_file",
        "signed_at",
    )

    def download_file(self, instance):
        if instance.files:
            if file_link := instance.files[0].get("files")[0].get("aws"):
                return mark_safe(f'<a class="grp-button" href={file_link} target="blank">Ссылка на файл</a>')
        else:
            return "-"

    download_file.short_description = "Скачать файл"
