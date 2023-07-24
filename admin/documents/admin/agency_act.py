from django.contrib import admin
from django.utils.html import mark_safe

from ..models import AgencyAct


@admin.register(AgencyAct)
class AgencyActAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "template_name",
        "agency",
        "project",
        "booking",
        "signed_at",
        "status",
        "get_agent_on_list",
    )
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
    autocomplete_fields = (
        "project",
        "booking",
        "agency",
    )
    search_fields = (
        "template_name",
        "agency__name",
        "agency__amocrm_id",
        "agency__inn",
        "project__name",
        "booking__agent__name",
        "booking__agent__surname",
        "booking__agent__patronymic",
        "booking__agent__amocrm_id",
        "status__name",
        "booking__amocrm_id",
        "booking__id",
    )

    def get_agent_on_list(self, obj):
        if obj.booking and obj.booking.agent:
            return f"{obj.booking.agent.amocrm_id} {obj.booking.agent.full_name}"
        else:
            return "-"

    get_agent_on_list.short_description = 'Ответственный агент'
    get_agent_on_list.admin_order_field = 'booking__agent'

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
