from django.contrib import admin

from privilege_program.models import PrivilegeFeedbackEmail


@admin.register(PrivilegeFeedbackEmail)
class PrivilegeFeedbackEmailAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "full_name",
    )
    readonly_fields = ("updated_at", "created_at",)
    exclude = ("feedback_settings",)
