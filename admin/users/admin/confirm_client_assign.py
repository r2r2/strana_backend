from django.contrib.admin import register, ModelAdmin

from users.models import ConfirmClientAssign


@register(ConfirmClientAssign)
class ConfirmClientAssignAdmin(ModelAdmin):
    list_display = (
        "id",
        "client",
        "agent",
        "agency",
        "assigned_at",
        "assign_confirmed_at",
        "unassigned_at",
    )
    list_filter = (
        "client",
        "agent",
        "agency",
        "assigned_at",
        "assign_confirmed_at",
        "unassigned_at",
    )
    search_fields = (
        "agent__name",
        "agent__surname",
        "agent__patronymic",
        "client__name",
        "client__surname",
        "client__patronymic",
        "agency__name",
    )
    save_on_top = True
    list_per_page = 15
