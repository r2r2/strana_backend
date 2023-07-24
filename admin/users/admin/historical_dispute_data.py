from django.contrib import admin
from django.contrib.admin import register

from users.models import HistoricalDisputeData


@register(HistoricalDisputeData)
class HistoricalDisputeDataAdmin(admin.ModelAdmin):
    list_display = (
        "dispute_agent",
        "dispute_agent_agency",
        "client",
        "client_agency",
        "agent",
        "dispute_requested",
    )
    readonly_fields = (
        "admin",
        "dispute_requested",
        'admin_update',
    )
    list_filter = (
        "dispute_requested",
    )
    search_fields = (
        "client__amocrm_id",
        "client__name",
        "client__surname",
        "client__patronymic",
        "client__phone",
        "agent__amocrm_id",
        "agent__name",
        "agent__surname",
        "agent__patronymic",
        "agent__phone",
        "client_agency__name",
        "client_agency__inn",
        "client_agency__amocrm_id",
        "dispute_agent__amocrm_id",
        "dispute_agent__name",
        "dispute_agent__surname",
        "dispute_agent__patronymic",
        "dispute_agent__phone",
        "dispute_agent_agency__name",
        "dispute_agent_agency__inn",
        "dispute_agent_agency__amocrm_id",
        "admin__name",
        "admin__surname",
        "admin__patronymic",
    )

    def save_model(self, request, obj, form, change):
        obj.admin_id = request.user.id
        super().save_model(request, obj, form, change)


