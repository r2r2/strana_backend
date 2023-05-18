from django.contrib.admin import register, ModelAdmin

from users.models import ConfirmClientAssign


@register(ConfirmClientAssign)
class ConfirmClientAssignAdmin(ModelAdmin):
    list_display = (
        "id",
        "__str__",
        "agency",
        "assigned_at",
        "assign_confirmed_at",
        "unassigned_at",
    )
    list_filter = ("__str__", "agency", "assigned_at", "assign_confirmed_at", "unassigned_at")
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
