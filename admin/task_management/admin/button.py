from django.contrib import admin

from task_management.models import Button


@admin.register(Button)
class ButtonAdmin(admin.ModelAdmin):
    list_display = (
        "label",
        "style",
        "slug",
        "status",
        "priority",
    )
    readonly_fields = ("updated_at", "created_at")
