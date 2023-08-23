from django.contrib.admin import register, ModelAdmin

from ..models import ConfirmClientAssign


@register(ConfirmClientAssign)
class ConfirmClientAssignAdmin(ModelAdmin):
    list_display = (
        "id",
        "client",
        "agent",
        "agency",
        "agency_type",
        "assigned_at",
        "assign_confirmed_at",
        "unassigned_at",
    )
    list_filter = (
        "client",
        "agent",
        "agency",
        "agency__general_type",
        "assigned_at",
        "assign_confirmed_at",
        "unassigned_at",
    )
    readonly_fields = (
        "client",
        "agent",
        "agency",
        "assigned_at",
        "assign_confirmed_at",
        "unassigned_at",
        "comment",
        "agency_type",
    )
    search_fields = (
        "agent__name",
        "agent__phone",
        "agent__surname",
        "agent__patronymic",
        "agent__amocrm_id",
        "client__name",
        "client__phone",
        "client__surname",
        "client__patronymic",
        "client__amocrm_id",
        "agency__name",
        "agency__inn",
        "agency__amocrm_id",
    )
    autocomplete_fields = (
        "agent",
        "agency",
        "client",
    )
    date_hierarchy = "assigned_at"
    save_on_top = True
    list_per_page = 15

    def agency_type(self, obj):
        if obj.agency:
            return obj.agency.general_type.label if obj.agency.general_type else "-"
        else:
            return "-"

    agency_type.short_description = 'Тип агентства'
    agency_type.admin_order_field = 'agency__general_type__sort'
